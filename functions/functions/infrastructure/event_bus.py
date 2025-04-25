import logging
from typing import Callable, Protocol, TypeVar

from functions.shared.domain_events import DomainEvent

Handler = Callable[[DomainEvent], None]


class IEventBus(Protocol):
    """Interface for an event bus."""

    def publish(self, event: DomainEvent) -> None: """
Publishes a domain event to all registered handlers for its type.

Raises:
    ValueError: If no handlers are registered for the event's type.
"""
...


class LocalEventBus:
    def __init__(
        self,
        handlers: dict[type[DomainEvent], list[Handler]],
    ) -> None:
        """
        Initializes a LocalEventBus with a mapping of event types to handler functions.
        
        Args:
            handlers: A dictionary mapping each DomainEvent type to a list of handler functions that will process events of that type.
        """
        self.handlers: dict[type[DomainEvent], list[Handler]] = handlers
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"{self.__class__.__name__} initialized")

    def publish(self, event: DomainEvent) -> None:
        """
        Dispatches a domain event to all registered handlers for its type.
        
        Raises:
            ValueError: If no handlers are registered for the event's type.
        """
        if event.__class__ not in self.handlers:
            # Note : Crashing here counter the event pattern philosophy, but for now
            # it's better than silently ignoring the event.
            raise ValueError(f"No handler registered for event type: {event.__class__}")
        for handler in self.handlers[event.__class__]:
            self.logger.info(f"Publishing event {event.__class__} to handler {handler}")
            try:
                handler(event)
            except Exception as e:
                self.logger.error(f"Error handling event {event.__class__}: {e}")


T = TypeVar("T", bound=DomainEvent)


class MockEventBus(IEventBus):
    """
    A mock implementation of the event bus for testing purposes.
    It records published events instead of dispatching them to handlers.
    """

    def __init__(self):
        """
        Initializes a MockEventBus for recording published domain events during testing.
        """
        self.published_events: list[DomainEvent] = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("MockEventBus initialized")

    def publish(self, event: DomainEvent) -> None:
        """
        Records a published event for later inspection instead of dispatching it.
        
        Args:
            event: The domain event to record.
        """
        event_type = type(event)
        self.logger.info(f"Mock publish called with event: {event_type.__name__}")
        self.published_events.append(event)

    # --- Helper methods for assertions ---

    def get_published_events(self) -> list[DomainEvent]:
        """
        Returns a shallow copy of all events that have been published.
        """
        return self.published_events[:]

    def clear_events(self) -> None:
        """
        Removes all recorded events from the mock event bus.
        """
        self.logger.debug("Clearing published events")
        self.published_events = []

    def get_last_event(self) -> DomainEvent | None:
        """
        Returns the most recently published event, or None if no events have been published.
        """
        return self.published_events[-1] if self.published_events else None

    def find_event(self, event_type: type[T]) -> T | None:
        """
        Returns the first published event of the specified type, or None if not found.
        
        Args:
            event_type: The class of the event to search for.
        
        Returns:
            The first event instance matching the given type, or None if no such event was published.
        """
        return next(
            (event for event in self.published_events if isinstance(event, event_type)),
            None,
        )

    def find_events(self, event_type: type[T]) -> list[T]:
        """
        Returns all published events matching the specified type.
        
        Args:
            event_type: The class of events to search for.
        
        Returns:
            A list of published events that are instances of the given type.
        """
        return [
            event for event in self.published_events if isinstance(event, event_type)
        ]

    def assert_event_published(
        self, event_type: type[DomainEvent], count: int = 1
    ) -> None:
        """
        Asserts that exactly the specified number of events of a given type were published.
        
        Args:
            event_type: The class of the event to check for.
            count: The expected number of published events of the given type.
        
        Raises:
            AssertionError: If the number of published events of the specified type does not match the expected count.
        """
        matching_events = self.find_events(event_type)
        assert (
            len(matching_events) == count
        ), f"Expected {count} event(s) of type {event_type.__name__}, but found {len(matching_events)}. Events: {self.published_events}"

    def assert_no_events_published(self) -> None:
        """
        Asserts that no events have been published.
        
        Raises an AssertionError if any events are present in the published events list.
        """
        assert (
            len(self.published_events) == 0
        ), f"Expected no events to be published, but found {len(self.published_events)}. Events: {self.published_events}"

    def assert_event_published_with_data(
        self, event_type: type[DomainEvent], **kwargs
    ) -> None:
        """
        Asserts that a published event of the specified type has attributes matching the given values.
        
        Raises an assertion error if no such event was published or if any attribute does not match the expected value.
        """
        found_event = self.find_event(event_type)
        assert (
            found_event is not None
        ), f"Event of type {event_type.__name__} not published. Events: {self.published_events}"

        for key, expected_value in kwargs.items():
            actual_value = getattr(found_event, key, None)
            assert (
                actual_value == expected_value
            ), f"Event {event_type.__name__} attribute '{key}' expected '{expected_value}', but got '{actual_value}'"
