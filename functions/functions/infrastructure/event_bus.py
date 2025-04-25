import logging
from typing import Callable

from functions.services.dev_notification_service import IDevNotificationService
from functions.shared import domain_events
from functions.synchronizer.ics_cache import IcsFileStorage

Handler = Callable[[domain_events.DomainEvent], None]


class LocalEventBus:
    def __init__(
        self,
        ics_file_storage: IcsFileStorage,
        dev_notification_service: IDevNotificationService,
    ) -> None:
        self.handlers: dict[type[domain_events.DomainEvent], list[Handler]] = HANDLERS
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("SimpleEventBus initialized")
        self.ics_file_storage = ics_file_storage
        self.dev_notification_service = dev_notification_service

    def publish(self, event: domain_events.DomainEvent) -> None:
        if event.__class__ not in self.handlers:
            raise ValueError(f"No handler registered for event type: {event.__class__}")
        for handler in self.handlers[event.__class__]:
            self.logger.info(f"Publishing event {event.__class__} to handler {handler}")
            try:
                handler(event)
            except Exception as e:
                self.logger.error(f"Error handling event {event.__class__}: {e}")


def handle_ics_fetched(
    event: domain_events.IcsFetched,
    *,
    ics_file_storage: IcsFileStorage,
) -> None:
    ics_file_storage.save_to_cache(
        ics_str=event.ics_str,
        metadata=event.context,
    )


def handle_sync_profile_created(
    event: domain_events.SyncProfileCreated,
    *,
    dev_notification_service: IDevNotificationService,
) -> None:
    dev_notification_service.on_new_sync_profile(event)


def handle_user_created(
    event: domain_events.UserCreated,
    *,
    dev_notification_service: IDevNotificationService,
) -> None:
    dev_notification_service.on_new_user(event)


def handle_sync_failed(
    event: domain_events.SyncFailed,
    *,
    dev_notification_service: IDevNotificationService,
) -> None:
    dev_notification_service.on_sync_failed(event)


HANDLERS: dict[type[domain_events.DomainEvent], list[Handler]] = {
    domain_events.IcsFetched: [handle_ics_fetched],
    domain_events.SyncProfileCreated: [handle_sync_profile_created],
    domain_events.UserCreated: [handle_user_created],
    domain_events.SyncFailed: [handle_sync_failed],
}  # type: ignore
