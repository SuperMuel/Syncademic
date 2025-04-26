from functions.repositories.sync_stats_repository import ISyncStatsRepository
from functions.services.dev_notification_service import IDevNotificationService
from functions.shared.domain_events import (
    IcsFetched,
    SyncFailed,
    SyncProfileCreated,
    SyncSucceeded,
    UserCreated,
    SyncProfileDeletionFailed,
)
from functions.synchronizer.ics_cache import IcsFileStorage


def handle_ics_fetched(event: IcsFetched, ics_file_storage: IcsFileStorage) -> None:
    ics_file_storage.save_to_cache(
        ics_str=event.ics_str,
        metadata=event.metadata,
    )


def handle_sync_profile_created(
    event: SyncProfileCreated,
    dev_notification_service: IDevNotificationService,
) -> None:
    dev_notification_service.on_new_sync_profile(event)


def handle_user_created(
    event: UserCreated,
    dev_notification_service: IDevNotificationService,
) -> None:
    dev_notification_service.on_new_user(event)


def handle_sync_failed(
    event: SyncFailed,
    dev_notification_service: IDevNotificationService,
) -> None:
    dev_notification_service.on_sync_failed(event)


def handle_sync_succeeded(
    event: SyncSucceeded,
    sync_stats_repo: ISyncStatsRepository,
) -> None:
    sync_stats_repo.increment_sync_count(
        user_id=event.user_id,
    )


def handle_sync_profile_deletion_failed(
    event: SyncProfileDeletionFailed,
    dev_notification_service: IDevNotificationService,
) -> None:
    dev_notification_service.on_sync_profile_deletion_failed(event)
