from datetime import datetime, timezone
import arrow

from functions.shared.event import Event
from functions.shared.google_calendar_colors import GoogleEventColor
from .mock_google_calendar_manager import (
    MockGoogleCalendarManager,
)


def test_create_and_retrieve_events():
    # Arrange
    manager = MockGoogleCalendarManager()
    sync_profile_id = "test_profile"

    events = [
        Event(
            start=arrow.get("2024-01-01T09:00:00+00:00"),
            end=arrow.get("2024-01-01T10:00:00+00:00"),
            title="Test Event 1",
            description="Description 1",
            color=GoogleEventColor.TOMATO,
        ),
        Event(
            start=arrow.get("2024-01-02T09:00:00+00:00"),
            end=arrow.get("2024-01-02T10:00:00+00:00"),
            title="Test Event 2",
            description="Description 2",
        ),
    ]

    # Act
    manager.create_events(events=events, sync_profile_id=sync_profile_id)
    event_ids = manager.get_events_ids_from_sync_profile(
        sync_profile_id=sync_profile_id
    )

    # Assert
    assert len(event_ids) == 2
    stored_events = manager.get_all_events()
    assert len(stored_events) == 2

    # Verify event details were stored correctly
    first_event = stored_events["1"][0]
    assert first_event["summary"] == "Test Event 1"
    assert first_event["colorId"] == GoogleEventColor.TOMATO.to_color_id()


def test_delete_events():
    # Arrange
    manager = MockGoogleCalendarManager()
    sync_profile_id = "test_profile"

    events = [
        Event(
            start=arrow.get("2024-01-01T09:00:00+00:00"),
            end=arrow.get("2024-01-01T10:00:00+00:00"),
            title="Test Event",
        ),
    ]

    # Act
    manager.create_events(events=events, sync_profile_id=sync_profile_id)
    event_ids = manager.get_events_ids_from_sync_profile(
        sync_profile_id=sync_profile_id
    )
    manager.delete_events(event_ids)

    # Assert
    assert len(manager.get_all_events()) == 0


def test_get_events_with_min_dt():
    # Arrange
    manager = MockGoogleCalendarManager()
    sync_profile_id = "test_profile"

    events = [
        Event(
            start=arrow.get("2024-01-01T09:00:00+00:00"),
            end=arrow.get("2024-01-01T10:00:00+00:00"),
            title="Past Event",
        ),
        Event(
            start=arrow.get("2024-02-01T09:00:00+00:00"),
            end=arrow.get("2024-02-01T10:00:00+00:00"),
            title="Future Event",
        ),
    ]

    manager.create_events(events=events, sync_profile_id=sync_profile_id)

    # Act
    min_dt = datetime(2024, 1, 15, tzinfo=timezone.utc)
    event_ids = manager.get_events_ids_from_sync_profile(
        sync_profile_id=sync_profile_id, min_dt=min_dt
    )

    # Assert
    assert len(event_ids) == 1
    stored_events = manager.get_all_events()
    assert stored_events[event_ids[0]][0]["summary"] == "Future Event"


def test_get_events_filters_by_sync_profile():
    # Arrange
    manager = MockGoogleCalendarManager()
    profile_1 = "profile_1"
    profile_2 = "profile_2"

    events_profile_1 = [
        Event(
            start=arrow.get("2024-01-01T09:00:00+00:00"),
            end=arrow.get("2024-01-01T10:00:00+00:00"),
            title="Profile 1 Event 1",
        ),
        Event(
            start=arrow.get("2024-01-02T09:00:00+00:00"),
            end=arrow.get("2024-01-02T10:00:00+00:00"),
            title="Profile 1 Event 2",
        ),
    ]

    events_profile_2 = [
        Event(
            start=arrow.get("2024-01-01T14:00:00+00:00"),
            end=arrow.get("2024-01-01T15:00:00+00:00"),
            title="Profile 2 Event",
        ),
    ]

    # Create events for both profiles
    manager.create_events(events=events_profile_1, sync_profile_id=profile_1)
    manager.create_events(events=events_profile_2, sync_profile_id=profile_2)

    # Act
    profile_1_events = manager.get_events_ids_from_sync_profile(
        sync_profile_id=profile_1
    )
    profile_2_events = manager.get_events_ids_from_sync_profile(
        sync_profile_id=profile_2
    )

    # Assert
    assert len(profile_1_events) == 2
    assert len(profile_2_events) == 1

    events_ids_1 = manager.get_events_ids_from_sync_profile(sync_profile_id=profile_1)
    events_ids_2 = manager.get_events_ids_from_sync_profile(sync_profile_id=profile_2)

    assert len(events_ids_1) == 2
    assert len(events_ids_2) == 1

    assert events_ids_1 == profile_1_events
    assert events_ids_2 == profile_2_events
