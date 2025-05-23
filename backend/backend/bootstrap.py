from functools import partial
from typing import cast
from backend import handlers
from backend.infrastructure.event_bus import LocalEventBus, Handler
from backend.repositories.sync_stats_repository import ISyncStatsRepository
from backend.services.dev_notification_service import IDevNotificationService
from backend.shared.domain_events import (
    DomainEvent,
    IcsFetched,
    RulesetGenerationFailed,
    SyncFailed,
    SyncProfileCreated,
    SyncSucceeded,
    UserCreated,
    SyncProfileDeletionFailed,
    SyncProfileCreationFailed,
)
from backend.synchronizer.ics_cache import IcsFileStorage


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
                        handlers.save_ics_to_storage,
                        ics_file_storage=ics_file_storage,
                    )
                ],
                SyncFailed: [
                    partial(
                        handlers.notify_developer_on_sync_failure,
                        dev_notification_service=dev_notification_service,
                    )
                ],
                SyncProfileCreated: [
                    partial(
                        handlers.notify_developer_on_sync_profile_creation,
                        dev_notification_service=dev_notification_service,
                    )
                ],
                UserCreated: [
                    partial(
                        handlers.notify_developer_on_new_user,
                        dev_notification_service=dev_notification_service,
                    )
                ],
                SyncSucceeded: [
                    partial(
                        handlers.increment_sync_count_on_sync_success,
                        sync_stats_repo=sync_stats_repo,
                    )
                ],
                SyncProfileDeletionFailed: [
                    partial(
                        handlers.notify_developer_on_sync_profile_deletion_failure,
                        dev_notification_service=dev_notification_service,
                    )
                ],
                SyncProfileCreationFailed: [
                    partial(
                        handlers.notify_developer_on_sync_profile_creation_failure,
                        dev_notification_service=dev_notification_service,
                    )
                ],
                RulesetGenerationFailed: [
                    partial(
                        handlers.notify_developer_on_ruleset_generation_failure,
                        dev_notification_service=dev_notification_service,
                    )
                ],
            },
        )
    )
