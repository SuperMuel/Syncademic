import logging
from typing import Callable, Protocol

from functions.services.dev_notification_service import IDevNotificationService
from functions.shared import domain_events
from functions.synchronizer.ics_cache import IcsFileStorage

Handler = Callable[[domain_events.DomainEvent], None]


class IEventBus(Protocol):
    """Interface for an event bus."""

    def publish(self, event: domain_events.DomainEvent) -> None: ...


class LocalEventBus:
    def __init__(
        self,
        ics_file_storage: IcsFileStorage,
        dev_notification_service: IDevNotificationService,
    ) -> None:
        self.handlers: dict[type[domain_events.DomainEvent], list[Handler]] = HANDLERS
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"{self.__class__.__name__} initialized")
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


class MockEventBus(IEventBus):
    """
    A mock implementation of the event bus for testing purposes.
    It records published events instead of dispatching them to handlers.
    """

    def __init__(self):
        self.published_events: list[domain_events.DomainEvent] = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("MockEventBus initialized")

    def publish(self, event: domain_events.DomainEvent) -> None:
        """Records the event instead of dispatching."""
        event_type = type(event)
        self.logger.info(f"Mock publish called with event: {event_type.__name__}")
        self.published_events.append(event)

    # --- Helper methods for assertions ---

    def get_published_events(self) -> list[domain_events.DomainEvent]:
        """Returns a copy of the list of published events."""
        return self.published_events[:]

    def clear_events(self) -> None:
        """Clears the list of recorded events."""
        self.logger.debug("Clearing published events")
        self.published_events = []

    def get_last_event(self) -> domain_events.DomainEvent | None:
        """Returns the last published event, or None if none were published."""
        return self.published_events[-1] if self.published_events else None

    def find_event(
        self, event_type: type[domain_events.DomainEvent]
    ) -> domain_events.DomainEvent | None:
        """Finds the first published event of a specific type."""
        return next(
            (event for event in self.published_events if isinstance(event, event_type)),
            None,
        )

    def find_events(
        self, event_type: type[domain_events.DomainEvent]
    ) -> list[domain_events.DomainEvent]:
        """Finds all published events of a specific type."""
        return [
            event for event in self.published_events if isinstance(event, event_type)
        ]

    def assert_event_published(
        self, event_type: type[domain_events.DomainEvent], count: int = 1
    ) -> None:
        """Asserts that exactly 'count' events of the specified type were published."""
        matching_events = self.find_events(event_type)
        assert (
            len(matching_events) == count
        ), f"Expected {count} event(s) of type {event_type.__name__}, but found {len(matching_events)}. Events: {self.published_events}"

    def assert_no_events_published(self) -> None:
        """Asserts that no events were published."""
        assert (
            len(self.published_events) == 0
        ), f"Expected no events to be published, but found {len(self.published_events)}. Events: {self.published_events}"

    def assert_event_published_with_data(
        self, event_type: type[domain_events.DomainEvent], **kwargs
    ) -> None:
        """Asserts that an event of the specified type was published and contains the specified data."""
        found_event = self.find_event(event_type)
        assert (
            found_event is not None
        ), f"Event of type {event_type.__name__} not published. Events: {self.published_events}"

        for key, expected_value in kwargs.items():
            actual_value = getattr(found_event, key, None)
            assert (
                actual_value == expected_value
            ), f"Event {event_type.__name__} attribute '{key}' expected '{expected_value}', but got '{actual_value}'"


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
