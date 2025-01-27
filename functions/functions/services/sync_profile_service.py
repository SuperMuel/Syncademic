import datetime
from dataclasses import replace
from typing import Any

from firebase_functions import logger

from functions.functions.services.exceptions.sync import (
    DailySyncLimitExceededError,
    SyncProfileNotFoundError,
)
from functions.functions.shared.google_calendar_colors import GoogleEventColor
from functions.models import (
    SyncProfile,
    SyncProfileStatus,
    SyncProfileStatusType,
    SyncTrigger,
    SyncType,
)
from functions.repositories.sync_profile_repository import ISyncProfileRepository
from functions.repositories.sync_stats_repository import ISyncStatsRepository
from functions.services.authorization_service import AuthorizationService
from functions.settings import settings
from functions.synchronizer.google_calendar_manager import GoogleCalendarManager
from functions.synchronizer.ics_cache import IcsFileStorage
from functions.synchronizer.ics_parser import IcsParser


class SyncProfileService:
    """
    Handles high-level domain logic for managing a user's SyncProfile lifecycle,
    including synchronization and deletion.
    """

    def __init__(
        self,
        *,
        sync_profile_repo: ISyncProfileRepository,
        sync_stats_repo: ISyncStatsRepository,
        authorization_service: AuthorizationService,
        ics_parser: IcsParser,
        ics_cache: IcsFileStorage,
        calendar_manager: GoogleCalendarManager,
    ) -> None:
        self._sync_profile_repo = sync_profile_repo
        self._sync_stats_repo = sync_stats_repo
        self._authorization_service = authorization_service
        self._ics_parser = ics_parser
        self._ics_cache = ics_cache
        self._calendar_manager = calendar_manager

    @staticmethod
    def _can_sync(status_type: SyncProfileStatusType) -> bool:
        match status_type:
            case (
                SyncProfileStatusType.IN_PROGRESS
                | SyncProfileStatusType.DELETING
                | SyncProfileStatusType.DELETION_FAILED
                #  Even if it's not actually deleted, we don't want to sync
                #  because the user intent was to delete the profile
            ):
                return False
            case (
                SyncProfileStatusType.NOT_STARTED
                | SyncProfileStatusType.FAILED  # Allow re-trying
                | SyncProfileStatusType.SUCCESS  # Allow re-syncing
            ):
                return True  # We allow trying again
            # case _: # Don't use a catch-all case ! we want to get warning if we forgot to add a case

    def synchronize(
        self,
        user_id: str,
        sync_profile_id: str,
        sync_trigger: SyncTrigger,
        sync_type: SyncType = SyncType.REGULAR,
    ) -> None:
        """
        Synchronizes a user's schedule with their target calendar.

        This method:
        1. Verifies the SyncProfile status to ensure it can be synchronized.
        2. Sets the profile status to IN_PROGRESS if allowable.
        3. Enforces the user's daily synchronization limit.
        4. Obtains an authorized Google Calendar manager for the target calendar.
        5. Fetches and parses the ICS data from the user's specified schedule source.
        6. Applies any defined customization rules (AI ruleset) to the events.
        7. Deletes or replaces relevant events on the target calendar based on the sync type:
            - REGULAR: Only future events are updated, leaving past events untouched.
            - FULL: All events previously created by this profile are removed and replaced.
            Note: This parameter is irrelevant for the first sync, which is always a full sync.
        8. Updates the SyncProfile status, marks a successful sync time,
            and increments the daily usage count on success.

        Args:
            user_id: The Firebase Auth user ID.
            sync_profile_id: The ID of the SyncProfile to synchronize.
            sync_trigger: Describes what triggered this sync (e.g., MANUAL, SCHEDULED).
            sync_type: Specifies whether to do a REGULAR or FULL synchronization.

        Raises:
            SyncProfileNotFoundError: If the SyncProfile does not exist.
        """
        assert user_id, "User ID must not be empty"
        assert sync_profile_id, "Sync profile ID must not be empty"

        profile = self._get_profile_or_raise(user_id, sync_profile_id)

        def _update_status(
            status_type: SyncProfileStatusType, error_message: str | None = None
        ) -> None:
            self._sync_profile_repo.update_sync_profile_status(
                user_id=user_id,
                sync_profile_id=sync_profile_id,
                status=SyncProfileStatus(
                    type=status_type,
                    syncTrigger=sync_trigger,
                    syncType=sync_type,
                    message=error_message,
                ),
            )

        # If status is incompatible, skip
        if not self._can_sync(profile.status.type):
            logger.info(f"Synchronization is {profile.status.type}, skipping")
            return

        # Mark as IN_PROGRESS
        _update_status(
            SyncProfileStatusType.IN_PROGRESS
        )  # TODO : this should be an atomic operation

        # Enforce daily limit
        try:
            self._enforce_daily_sync_limit(user_id)
        except DailySyncLimitExceededError as e:
            _update_status(SyncProfileStatusType.FAILED, str(e))
            return

        try:
            service = self._authorization_service.get_calendar_service(
                user_id, profile.targetCalendar.providerAccountId
            )
        except Exception as e:
            logger.error(f"Failed to get calendar service: {e}")
            _update_status(SyncProfileStatusType.FAILED, str(e))
            return

        # Actually do the synchronization steps
        try:
            self._run_synchronization(
                profile=profile,
                user_id=user_id,
                sync_profile_id=sync_profile_id,
                sync_trigger=sync_trigger,
                sync_type=sync_type,
                service=service,
            )

            logger.info("Synchronization successful")
        except Exception as e:
            logger.error(f"Failed to sync: {e}")
            _update_status(SyncProfileStatusType.FAILED, str(e))
            return

        # On success
        _update_status(SyncProfileStatusType.SUCCESS)
        self._sync_profile_repo.update_last_successful_sync(user_id, sync_profile_id)
        self._sync_stats_repo.increment_sync_count(user_id)

        logger.info("Synchronization successful")

    def _run_synchronization(
        self,
        *,
        profile: SyncProfile,
        sync_trigger: SyncTrigger,
        sync_type: SyncType,
        user_id: str,
        sync_profile_id: str,
        service: Any,
    ) -> None:
        logger.info(f"Running synchronization for profile {profile.id}")

        def _save_ics_to_cache(
            ics_str: str,
            *,
            parsing_error: Exception | None = None,
        ) -> None:
            """
            Saves ICS string to cache, logging any errors without raising them.
            """
            try:
                self._ics_cache.save_to_cache(
                    ics_str=ics_str,
                    user_id=user_id,
                    sync_profile_id=sync_profile_id,
                    sync_trigger=sync_trigger,
                    ics_source=profile.scheduleSource.to_ics_source(),
                    parsing_error=parsing_error,
                )
            except Exception as e:
                logger.error(f"Failed to store ics string in firebase storage: {e}")
                # Do not raise, we want to continue the execution

        ics_str = profile.scheduleSource.to_ics_source().get_ics_string()
        logger.info(f"ICS string size: {len(ics_str) / 1024} KB")

        try:
            events = self._ics_parser.parse(ics_str)
        except Exception as e:
            logger.error(f"Failed to parse ics: {e}")
            # Save the ics string for later debugging
            _save_ics_to_cache(ics_str, parsing_error=e)
            raise e

        logger.info(f"Found {len(events)} events in ics")

        # Save the ics string for later debugging
        _save_ics_to_cache(ics_str)

        # Apply ruleset if any
        if profile.ruleset:
            try:
                logger.info(
                    "Temporary : since a ruleset is provided that will probably change colors, we will first manually set all the events to grey color"
                )
                events = [
                    replace(event, color=GoogleEventColor.GRAPHITE) for event in events
                ]
                logger.info(f"Applying {len(profile.ruleset.rules)} rules")
                events = profile.ruleset.apply(events)
                logger.info(f"{len(events)} events after applying rules")
            except Exception as e:
                logger.error(f"Failed to apply rules: {e}")
                raise e

        if not events:
            logger.warn("No events to synchronize")
            return

        # When it's the first sync, we create all the events on the target calendar
        # and that's all we need to do
        if sync_trigger == SyncTrigger.ON_CREATE:
            return self._calendar_manager.create_events(
                events,
                service=service,
                calendar_id=profile.targetCalendar.id,
                sync_profile_id=profile.id,
            )

        match sync_type:
            case SyncType.REGULAR:
                # When it's a regular sync, we only update future events, and let past events untouched
                separation_dt = datetime.now(datetime.timezone.utc)
                to_create = [event for event in events if event.end > separation_dt]
                to_delete = self._calendar_manager.get_events_ids_from_sync_profile(
                    service=service,
                    calendar_id=profile.targetCalendar.id,
                    sync_profile_id=profile.id,
                    min_dt=separation_dt,
                )
            case SyncType.FULL:
                # When it's a full sync, we delete all the events on the target calendar linked
                # to this sync profile and then create all the events again
                to_delete = self._calendar_manager.get_events_ids_from_sync_profile(
                    service=service,
                    calendar_id=profile.targetCalendar.id,
                    sync_profile_id=profile.id,
                    min_dt=None,
                )
                to_create = events

        if to_delete:
            logger.info(f"Found {len(to_delete)} events to delete")
            self._calendar_manager.delete_events(
                ids=to_delete,
                service=service,
                calendar_id=profile.targetCalendar.id,
            )
        else:
            logger.info("No events to delete")

        if to_create:
            logger.info(f"Found {len(to_create)} events to create")
            calendar_manager.create_events(to_create, profile.id)
        else:
            logger.info("No new events to create")

    def _get_profile_or_raise(self, user_id: str, sync_profile_id: str) -> SyncProfile:
        profile = self._sync_profile_repo.get_sync_profile(user_id, sync_profile_id)
        if profile is None:
            raise SyncProfileNotFoundError(
                f"Sync profile not found for user {user_id} and sync profile ID {sync_profile_id}"
            )
        return profile

    def _enforce_daily_sync_limit(
        self,
        user_id: str,
    ) -> None:
        """
        Enforces the daily synchronization limit for a user.

        Raises:
            DailySyncLimitExceededError: If the user has reached their daily sync limit
        """
        sync_count = self._sync_stats_repo.get_daily_sync_count(user_id)
        logger.info(f"Sync count for today: {sync_count}")

        if sync_count >= settings.MAX_SYNCHRONIZATIONS_PER_DAY:
            logger.info(f"User {user_id} has reached the daily synchronization limit.")
            raise DailySyncLimitExceededError(
                f"Daily synchronization limit of {settings.MAX_SYNCHRONIZATIONS_PER_DAY} reached."
            )
