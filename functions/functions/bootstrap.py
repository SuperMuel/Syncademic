from functools import partial
from typing import cast
from functions import handlers
from functions.infrastructure.event_bus import LocalEventBus, Handler
from functions.repositories.sync_stats_repository import ISyncStatsRepository
from functions.services.dev_notification_service import IDevNotificationService
from functions.shared.domain_events import (
    DomainEvent,
    IcsFetched,
    SyncFailed,
    SyncProfileCreated,
    SyncSucceeded,
    UserCreated,
    SyncProfileDeletionFailed,
)
from functions.synchronizer.ics_cache import IcsFileStorage


def bootstrap_event_bus(
    ics_file_storage: IcsFileStorage,
    dev_notification_service: IDevNotificationService,
    sync_stats_repo: ISyncStatsRepository,
) -> LocalEventBus:
    return LocalEventBus(
        handlers=cast(
            dict[type[DomainEvent], list[Handler]],
            {
                IcsFetched: [
                    partial(
                        handlers.handle_ics_fetched,
                        ics_file_storage=ics_file_storage,
                    )
                ],
                SyncFailed: [
                    partial(
                        handlers.handle_sync_failed,
                        dev_notification_service=dev_notification_service,
                    )
                ],
                SyncProfileCreated: [
                    partial(
                        handlers.handle_sync_profile_created,
                        dev_notification_service=dev_notification_service,
                    )
                ],
                UserCreated: [
                    partial(
                        handlers.handle_user_created,
                        dev_notification_service=dev_notification_service,
                    )
                ],
                SyncSucceeded: [
                    partial(
                        handlers.handle_sync_succeeded,
                        sync_stats_repo=sync_stats_repo,
                    )
                ],
                SyncProfileDeletionFailed: [
                    partial(
                        handlers.handle_sync_profile_deletion_failed,
                        dev_notification_service=dev_notification_service,
                    )
                ],
            },
        )
    )
