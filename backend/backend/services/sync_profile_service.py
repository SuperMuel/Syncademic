import logging
from dataclasses import replace
from datetime import datetime, timezone
import traceback
from typing import Callable
from uuid import uuid4

from backend.infrastructure.event_bus import IEventBus
from backend.models import (
    SyncProfile,
    SyncProfileStatus,
    SyncProfileStatusType,
    SyncTrigger,
    SyncType,
)
from backend.models.schemas import CreateSyncProfileInput
from backend.models.sync_profile import TargetCalendar
from backend.repositories.sync_profile_repository import ISyncProfileRepository
from backend.repositories.sync_stats_repository import ISyncStatsRepository
from backend.services.ai_ruleset_service import AiRulesetService
from backend.services.authorization_service import AuthorizationService
from backend.services.exceptions.ics import BaseIcsError, IcsParsingError
from backend.services.exceptions.sync import (
    DailySyncLimitExceededError,
    SyncProfileNotFoundError,
)
from backend.services.exceptions.target_calendar import TargetCalendarNotFoundError
from backend.services.google_calendar_service import GoogleCalendarService
from backend.services.ics_service import IcsService
from backend.settings import settings
from backend.shared import domain_events
from backend.shared.google_calendar_colors import GoogleEventColor
from backend.synchronizer.google_calendar_manager import GoogleCalendarManager
from backend.synchronizer.ics_source import UrlIcsSource

logger = logging.getLogger(__name__)


class SyncProfileService:
    """
    Handles high-level domain logic for managing a user's SyncProfile lifecycle,
    including synchronization and deletion.
    """

    def __init__(
        self,
        *,
        sync_profile_repo: ISyncProfileRepository,
        authorization_service: AuthorizationService,
        sync_stats_repo: ISyncStatsRepository,
        ics_service: IcsService,
        google_calendar_service: GoogleCalendarService,
        ai_ruleset_service: AiRulesetService,
        event_bus: IEventBus,
    ) -> None:
        self._sync_profile_repo = sync_profile_repo
        self._authorization_service = authorization_service
        self._sync_stats_repo = sync_stats_repo
        self._google_calendar_service = google_calendar_service
        self._ics_service = ics_service
        self._ai_ruleset_service = ai_ruleset_service
        self._event_bus = event_bus

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

            # If sync count is exceeded, raise DailySyncLimitExceededError
            self._enforce_daily_sync_limit(user_id)

        # Mark as IN_PROGRESS
        profile.status = _new_status(SyncProfileStatusType.IN_PROGRESS)
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

        except Exception as e:
            logger.error(f"Failed to sync: {e}")
            profile.status = _new_status(SyncProfileStatusType.FAILED, str(e))
            self._sync_profile_repo.save_sync_profile(profile)

            self._event_bus.publish(
                domain_events.SyncFailed(
                    user_id=user_id,
                    sync_profile_id=sync_profile_id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    formatted_traceback=traceback.format_exc(),
                )
            )

            return

        # On success
        profile.status = _new_status(SyncProfileStatusType.SUCCESS)
        profile.lastSuccessfulSync = datetime.now(timezone.utc)

        self._sync_profile_repo.save_sync_profile(profile)

        self._event_bus.publish(
            domain_events.SyncSucceeded(
                user_id=user_id,
                sync_profile_id=sync_profile_id,
            )
        )

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

        result_or_error = self._ics_service.try_fetch_and_parse(
            ics_source=profile.scheduleSource.to_ics_source(),
            metadata={
                "sync_profile_id": profile.id,
                "user_id": user_id,
                "sync_trigger": sync_trigger,
                "sync_type": sync_type,
                "source": profile.scheduleSource.model_dump(),
            },
        )
        if isinstance(result_or_error, BaseIcsError):
            raise result_or_error

        assert isinstance(events := result_or_error.events, list)

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
            logger.warning("No events to synchronize")
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
            self._event_bus.publish(
                domain_events.SyncProfileDeletionFailed(
                    user_id=user_id,
                    sync_profile_id=sync_profile_id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    formatted_traceback=traceback.format_exc(),
                )
            )
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
            self._event_bus.publish(
                domain_events.SyncProfileDeletionFailed(
                    user_id=user_id,
                    sync_profile_id=sync_profile_id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    formatted_traceback=traceback.format_exc(),
                )
            )

    def create_sync_profile(
        self,
        user_id: str,
        request: CreateSyncProfileInput,
        uuid_factory: Callable[[], str] | None = None,
    ) -> SyncProfile:
        """
        Creates a new SyncProfile based on user input, performing necessary
        validations and resource creation (like a new Google Calendar).

        Args:
            user_id: The Firebase Auth ID of the user.
            request: Validated input data containing profile details.

        Returns:
            The newly created SyncProfile object.

        Raises:
            UnauthorizedError: If the backend isn't authorized for the provider account.
            IcsSourceError: If the schedule source URL is invalid or inaccessible.
            TargetCalendarNotFoundError: If using an existing calendar and it's not found.
            TargetCalendarAccessError: If using an existing calendar and lack write permissions.
            SyncademicError: For other specific creation errors.
            Exception: For unexpected errors during the process.
        """
        try:
            logger.info(
                "Creating sync profile",
                extra={
                    "user_id": user_id,
                    "request_title": request.title,
                },
            )

            # Fetch Auth & Validate Provider Account
            self._authorization_service.test_authorization(
                user_id, request.targetCalendar.providerAccountId
            )
            logger.info(
                "Authorization test successful.",
                extra={
                    "user_id": user_id,
                    "provider_account_id": request.targetCalendar.providerAccountId,
                },
            )

            # Validate ICS URL
            ics_source = request.scheduleSource.to_ics_source()

            self._ics_service.validate_ics_url_or_raise(
                ics_source,
                metadata={"user_id": user_id, "context": "create_sync_profile"},
            )
            logger.info(
                "ICS URL validated successfully.",
                extra={
                    "user_id": user_id,
                    "url": str(ics_source.url)
                    if isinstance(ics_source, UrlIcsSource)
                    else None,
                },
            )

            sync_profile_id = uuid_factory() if uuid_factory else str(uuid4())

            # Handle Target Calendar
            if request.targetCalendar.type == "createNew":
                logger.info(
                    "Creating new target calendar.",
                    extra={"user_id": user_id},
                )
                cal_result = self._google_calendar_service.create_new_calendar(
                    user_id=user_id,
                    provider_account_id=request.targetCalendar.providerAccountId,
                    summary=request.title,
                    description=f"Syncademic calendar for '{request.title}' ({sync_profile_id=})",
                    color_id=request.targetCalendar.colorId,
                )
                calendar_id = cal_result["id"]
                calendar_title = cal_result.get("summary", request.title)
                calendar_description = cal_result.get("description", "")
                logger.info(
                    "New target calendar created.",
                    extra={
                        "user_id": user_id,
                        "calendar_id": calendar_id,
                    },
                )
            else:  # useExisting
                calendar_id = request.targetCalendar.calendarId
                logger.info(
                    f"Validating existing target calendar: {calendar_id}",
                    extra={"user_id": user_id},
                )
                found_calendar = self._google_calendar_service.get_calendar_by_id(
                    user_id=user_id,
                    provider_account_id=request.targetCalendar.providerAccountId,
                    calendar_id=calendar_id,
                )
                if not found_calendar:
                    raise TargetCalendarNotFoundError(
                        f"Calendar not found for ID: {calendar_id}"
                    )

                calendar_title = found_calendar.get("summary", "Untitled")
                calendar_description = found_calendar.get("description", "")
                logger.info(
                    "Existing target calendar validated.",
                    extra={
                        "user_id": user_id,
                        "calendar_id": calendar_id,
                        "title": calendar_title,
                    },
                )

            # Construct TargetCalendar Model
            target_calendar = TargetCalendar(
                id=calendar_id,
                title=calendar_title,
                description=calendar_description,
                providerAccountId=request.targetCalendar.providerAccountId,
                providerAccountEmail=self._authorization_service.get_provider_account_email(
                    user_id, request.targetCalendar.providerAccountId
                ),
            )

            # Construct SyncProfile Model
            sync_profile = SyncProfile(
                id=sync_profile_id,
                user_id=user_id,
                title=request.title,
                scheduleSource=request.scheduleSource,
                targetCalendar=target_calendar,
                status=SyncProfileStatus(type=SyncProfileStatusType.NOT_STARTED),
                # ruleset and ruleset_error are None initially
            )

            # Persist SyncProfile
            self._sync_profile_repo.save_sync_profile(sync_profile)
            logger.info(
                "SyncProfile persisted.",
                extra={
                    "user_id": user_id,
                    "sync_profile_id": sync_profile_id,
                },
            )

        except Exception as e:
            self._event_bus.publish(
                domain_events.SyncProfileCreationFailed(
                    user_id=user_id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    formatted_traceback=traceback.format_exc(),
                )
            )
            raise

        # 7. Generate initial ruleset
        # It does not raise any error so that even if it fails, the sync profile is still created
        self._ai_ruleset_service.create_ruleset_for_sync_profile(sync_profile)

        # 8. Publish Event
        self._event_bus.publish(
            domain_events.SyncProfileCreated(
                user_id=user_id,
                sync_profile_id=sync_profile_id,
            )
        )

        # 9. Launch initial sync
        try:
            self.synchronize(
                user_id=user_id,
                sync_profile_id=sync_profile_id,
                sync_trigger=SyncTrigger.ON_CREATE,
            )
        except Exception as e:
            logger.error(
                "Failed to perform initial sync after profile creation.",
                extra={
                    "user_id": user_id,
                    "sync_profile_id": sync_profile_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
            )
            # Let the normal flow continue, i.e returning the created sync profile.
            # Ideally, we shouldn't trigger the initial sync here, as it
            # violates the single responsibility principle.
            # TODO : react to the SyncProfileCreated event to initiate the first sync

        return sync_profile
