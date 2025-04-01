from dataclasses import replace
from datetime import datetime, timezone
from typing import Any

from firebase_functions import logger

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
from functions.services.exceptions.ics import BaseIcsError, IcsParsingError
from functions.services.exceptions.sync import (
    DailySyncLimitExceededError,
    SyncProfileNotFoundError,
)
from functions.services.ics_service import IcsService
from functions.settings import settings
from functions.shared.google_calendar_colors import GoogleEventColor
from functions.synchronizer.google_calendar_manager import GoogleCalendarManager
from functions.services.dev_notification_service import (
    IDevNotificationService,
    NoOpDevNotificationService,
)


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
        ics_service: IcsService,
        dev_notification_service: IDevNotificationService | None = None,
    ) -> None:
        self._sync_profile_repo = sync_profile_repo
        self._sync_stats_repo = sync_stats_repo
        self._authorization_service = authorization_service
        self._ics_service = ics_service
        self.dev_notification_service = (
            dev_notification_service or NoOpDevNotificationService()
        )

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
        force: bool = False,
    ) -> None:
        """
        Synchronizes a user's schedule with their target calendar.

        This method:
        1. Verifies the SyncProfile status to ensure it can be synchronized. Skip this step if `force` is True,
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

        def _new_status(
            status_type: SyncProfileStatusType, error_message: str | None = None
        ) -> SyncProfileStatus:
            return SyncProfileStatus(
                type=status_type,
                syncTrigger=sync_trigger,
                syncType=sync_type,
                message=error_message,
            )

        if force:
            logger.info("Force sync triggered")
        else:
            # If status is incompatible, skip
            if not self._can_sync(profile.status.type):
                logger.info(f"Synchronization is {profile.status.type}, skipping")
                return

        # Mark as IN_PROGRESS
        profile.status = _new_status(SyncProfileStatusType.IN_PROGRESS)
        self._sync_profile_repo.save_sync_profile(profile)

        # Enforce daily limit only if not force sync
        if not force:
            try:
                self._enforce_daily_sync_limit(user_id)
            except DailySyncLimitExceededError as e:
                profile.status = _new_status(SyncProfileStatusType.FAILED, str(e))
                self._sync_profile_repo.save_sync_profile(profile)
                return

        try:
            calendar_manager = (
                self._authorization_service.get_authenticated_google_calendar_manager(
                    user_id=user_id,
                    provider_account_id=profile.targetCalendar.providerAccountId,
                    calendar_id=profile.targetCalendar.id,
                )
            )
        except Exception as e:
            logger.error(f"Failed to get calendar service: {e}")
            profile.status = _new_status(SyncProfileStatusType.FAILED, str(e))
            self._sync_profile_repo.save_sync_profile(profile)
            return

        # Actually do the synchronization steps
        try:
            self._run_synchronization(
                profile=profile,
                user_id=user_id,
                sync_trigger=sync_trigger,
                sync_type=sync_type,
                calendar_manager=calendar_manager,
            )

            logger.info("Synchronization successful")
        except Exception as e:
            logger.error(f"Failed to sync: {e}")
            profile.status = _new_status(SyncProfileStatusType.FAILED, str(e))
            self._sync_profile_repo.save_sync_profile(profile)

            # Notify developers about the failure
            self.dev_notification_service.on_sync_failed(
                user_id=user_id,
                sync_profile_id=sync_profile_id,
                title=profile.title,
                error=e,
            )

            return

        # On success
        profile.status = _new_status(SyncProfileStatusType.SUCCESS)
        profile.lastSuccessfulSync = datetime.now(timezone.utc)

        self._sync_profile_repo.save_sync_profile(profile)
        self._sync_stats_repo.increment_sync_count(user_id)

        logger.info("Synchronization successful")

    def _run_synchronization(
        self,
        *,
        profile: SyncProfile,
        sync_trigger: SyncTrigger,
        sync_type: SyncType,
        user_id: str,
        calendar_manager: GoogleCalendarManager,
    ) -> None:
        logger.info(f"Running synchronization for profile {profile.id}")

        events_or_error = self._ics_service.try_fetch_and_parse(
            ics_source=profile.scheduleSource.to_ics_source(),
            metadata={
                "sync_profile_id": profile.id,
                "user_id": user_id,
                "sync_trigger": sync_trigger,
                "sync_type": sync_type,
            },
        )
        if not isinstance(error := events_or_error, list):
            raise error

        assert isinstance(events := events_or_error, list)

        logger.info(f"Found {len(events)} events in ics")

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
            return calendar_manager.create_events(
                events,
                sync_profile_id=profile.id,
            )

        match sync_type:
            case SyncType.REGULAR:
                # When it's a regular sync, we only update future events, and let past events untouched
                separation_dt = datetime.now(timezone.utc)
                to_create = [event for event in events if event.end > separation_dt]
                to_delete = calendar_manager.get_events_ids_from_sync_profile(
                    sync_profile_id=profile.id,
                    min_dt=separation_dt,
                )
            case SyncType.FULL:
                # When it's a full sync, we delete all the events on the target calendar linked
                # to this sync profile and then create all the events again
                to_delete = calendar_manager.get_events_ids_from_sync_profile(
                    sync_profile_id=profile.id,
                    min_dt=None,
                )
                to_create = events

        if to_delete:
            logger.info(f"Found {len(to_delete)} events to delete")
            calendar_manager.delete_events(
                ids=to_delete,
            )
        else:
            logger.info("No events to delete")

        if to_create:
            logger.info(f"Found {len(to_create)} events to create")
            calendar_manager.create_events(to_create, sync_profile_id=profile.id)
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

    def _can_delete(self, status_type: SyncProfileStatusType) -> bool:
        match status_type:
            case (
                SyncProfileStatusType.DELETING  # Already in deletion process
                | SyncProfileStatusType.DELETION_FAILED  # re-trying deletion is not implemented yet
                | SyncProfileStatusType.IN_PROGRESS  # Do not delete while synchronization is in progress
                | SyncProfileStatusType.NOT_STARTED  # A synchronization will start soon, so we don't delete
            ):
                return False
            case (
                SyncProfileStatusType.FAILED  # Failed syncs can be deleted
                | SyncProfileStatusType.SUCCESS  # Successful syncs can be deleteds
            ):
                return True
            # case _: # Don't use a catch-all case ! we want to get warning if we forgot to add a case

        raise ValueError(f"Unhandled status type: {status_type}")

    def delete_sync_profile(self, user_id: str, sync_profile_id: str) -> None:
        """
        Handles the complete deletion process for a sync profile including:
        1. Status validation and transition to DELETING state
        2. Calendar event cleanup
        3. Profile deletion from repository

        Args:
            user_id: Firebase Auth user ID
            sync_profile_id: ID of the sync profile to delete

        Doesn't raise but logs errors and updates the sync profile status to DELETION_FAILED
        in case of error.

        For a default deletion, we want to delete all the events on the target calendar. This
        step can fail because of a calendar authorization error or because of an error while
        deleting the events. Thus there's a need for a DELETION_FAILED status.
        Currently, we don't retry nor force the deletion, as we want to take time to think about
        how to handle this. Some users might want to delete their events but not the calendar, some
        might want to delete everything, some might want to just delete the sync profile but not the
        calendar or the events.  #TODO (supermuel) implement right deletion logic.
        """
        profile = self._get_profile_or_raise(user_id, sync_profile_id)

        if not self._can_delete(profile.status.type):
            logger.info(f"Profile is {profile.status.type}, skipping deletion")
            return

        profile.status = SyncProfileStatus(type=SyncProfileStatusType.DELETING)
        self._sync_profile_repo.save_sync_profile(profile)

        try:
            calendar_manager = (
                self._authorization_service.get_authenticated_google_calendar_manager(
                    user_id=user_id,
                    provider_account_id=profile.targetCalendar.providerAccountId,
                    calendar_id=profile.targetCalendar.id,
                )
            )
        except Exception as e:
            logger.error(f"Authorization failed: {e}")
            profile.status = SyncProfileStatus(
                type=SyncProfileStatusType.DELETION_FAILED,
                message=f"Authorization failed.",
            )
            self._sync_profile_repo.save_sync_profile(profile)
            return

        try:
            if to_delete_ids := calendar_manager.get_events_ids_from_sync_profile(
                sync_profile_id=profile.id
            ):
                logger.info(f"Deleting {len(to_delete_ids)} events")
                calendar_manager.delete_events(ids=to_delete_ids)
            else:
                logger.info("No events to delete")

            self._sync_profile_repo.delete_sync_profile(user_id, sync_profile_id)
            logger.info("Deletion successful")

        except Exception as e:
            logger.error(f"Unexpected error during event deletion: {e}")
            profile.status = SyncProfileStatus(
                type=SyncProfileStatusType.DELETION_FAILED,
                message=f"Could not delete events from calendar.",
            )
            self._sync_profile_repo.save_sync_profile(profile)
