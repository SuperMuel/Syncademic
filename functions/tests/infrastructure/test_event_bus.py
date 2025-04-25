import pytest
from unittest.mock import Mock

from functions.infrastructure.event_bus import LocalEventBus, MockEventBus
from functions.shared.domain_events import DomainEvent, IcsFetched, SyncFailed


def test_local_event_bus_dispatches_to_handler() -> None:
    called = {}

    def handler(event: DomainEvent) -> None:
        called["event"] = event

    bus = LocalEventBus(handlers={IcsFetched: [handler]})
    event = IcsFetched(ics_str="ICS", metadata={"foo": "bar"})
    bus.publish(event)
    assert called["event"] == event


def test_local_event_bus_multiple_handlers() -> None:
    calls: list[tuple[str, DomainEvent]] = []

    def handler1(event: DomainEvent) -> None:
        calls.append(("h1", event))

    def handler2(event: DomainEvent) -> None:
        calls.append(("h2", event))

    bus = LocalEventBus(handlers={IcsFetched: [handler1, handler2]})
    event = IcsFetched(ics_str="ICS", metadata=None)
    bus.publish(event)
    assert ("h1", event) in calls
    assert ("h2", event) in calls
    assert len(calls) == 2


def test_local_event_bus_raises_on_no_handler() -> None:
    bus = LocalEventBus(handlers={})
    event = IcsFetched(ics_str="ICS", metadata=None)
    with pytest.raises(ValueError, match="No handler registered for event type"):
        bus.publish(event)


def test_local_event_bus_logs_error_on_handler_exception(caplog) -> None:
    def bad_handler(event: DomainEvent) -> None:
        raise RuntimeError("fail!")

    bus = LocalEventBus(handlers={IcsFetched: [bad_handler]})
    event = IcsFetched(ics_str="ICS", metadata=None)
    with caplog.at_level("ERROR"):
        bus.publish(event)
    assert any("Error handling event" in m for m in caplog.text.splitlines())


def test_mock_event_bus_records_and_finds_events() -> None:
    bus = MockEventBus()
    event1 = IcsFetched(ics_str="A", metadata=None)
    event2 = SyncFailed(
        user_id="u",
        sync_profile_id="p",
        error_type="E",
        error_message="msg",
        formatted_traceback=None,
    )
    bus.publish(event1)
    bus.publish(event2)
    assert bus.get_published_events() == [event1, event2]
    assert bus.get_last_event() == event2
    assert bus.find_event(IcsFetched) == event1
    assert bus.find_events(SyncFailed) == [event2]


def test_mock_event_bus_assertions() -> None:
    bus = MockEventBus()
    event = IcsFetched(ics_str="A", metadata={"x": 1})
    bus.publish(event)
    bus.assert_event_published(IcsFetched)
    bus.assert_event_published_with_data(IcsFetched, ics_str="A", metadata={"x": 1})
    bus.clear_events()
    bus.assert_no_events_published()
