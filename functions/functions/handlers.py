from functions.models.sync_profile import SyncTrigger
from functions.repositories.sync_stats_repository import ISyncStatsRepository
from functions.services.dev_notification_service import IDevNotificationService
from functions.services.sync_profile_service import SyncProfileService
from functions.shared.domain_events import (
    IcsFetched,
    SyncFailed,
    SyncProfileCreated,
    SyncSucceeded,
    UserCreated,
    SyncProfileDeletionFailed,
)
from functions.synchronizer.ics_cache import IcsFileStorage


def save_ics_to_storage(event: IcsFetched, ics_file_storage: IcsFileStorage) -> None:
    ics_file_storage.save_to_cache(
        ics_str=event.ics_str,
        metadata=event.metadata,
    )


def notify_developer_on_sync_profile_creation(
    event: SyncProfileCreated,
    dev_notification_service: IDevNotificationService,
) -> None:
    dev_notification_service.on_new_sync_profile(event)


def notify_developer_on_new_user(
    event: UserCreated,
    dev_notification_service: IDevNotificationService,
) -> None:
    dev_notification_service.on_new_user(event)


def notify_developer_on_sync_failure(
    event: SyncFailed,
    dev_notification_service: IDevNotificationService,
) -> None:
    dev_notification_service.on_sync_failed(event)


def increment_sync_count_on_sync_success(
    event: SyncSucceeded,
    sync_stats_repo: ISyncStatsRepository,
) -> None:
    sync_stats_repo.increment_sync_count(
        user_id=event.user_id,
    )


def notify_developer_on_sync_profile_deletion_failure(
    event: SyncProfileDeletionFailed,
    dev_notification_service: IDevNotificationService,
) -> None:
    dev_notification_service.on_sync_profile_deletion_failed(event)
