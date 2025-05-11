from datetime import datetime, timezone
from unittest.mock import Mock

import arrow
from functions.shared.event import Event
from functions.shared.google_calendar_colors import GoogleEventColor
from functions.synchronizer.google_calendar_manager import GoogleCalendarManager


def test_event_to_google_event_basic():
    # Arrange
    service = Mock()
    calendar_id = "test_calendar_id"
    manager = GoogleCalendarManager(service=service, calendar_id=calendar_id)

    event = Event(
        start=arrow.get("2023-01-01T09:00:00+00:00"),
        end=arrow.get("2023-01-01T10:00:00+00:00"),
        title="Test Event",
        description="Test Description",
        location="Test Location",
        color=None,
    )
    extended_properties = {"private": {"syncademic": "sync_profile_id"}}

    # Act
    google_event = manager._event_to_google_event(event, extended_properties)

    # Assert
    assert google_event == {
        "summary": "Test Event",
        "description": "Test Description",
        "start": {"dateTime": "2023-01-01T09:00:00+00:00"},
        "end": {"dateTime": "2023-01-01T10:00:00+00:00"},
        "location": "Test Location",
        "extendedProperties": extended_properties,
    }


def test_event_to_google_event_with_color():
    # Arrange
    service = Mock()
    calendar_id = "test_calendar_id"
    manager = GoogleCalendarManager(service=service, calendar_id=calendar_id)

    color = GoogleEventColor.TOMATO

    event = Event(
        start=arrow.get("2023-01-01T09:00:00+00:00"),
        end=arrow.get("2023-01-01T10:00:00+00:00"),
        title="Colored Event",
        description="Event with color",
        location="Test Location",
        color=color,
    )
    extended_properties = {"private": {"syncademic": "sync_profile_id"}}

    # Act
    google_event = manager._event_to_google_event(event, extended_properties)

    # Assert
    assert google_event == {
        "summary": "Colored Event",
        "description": "Event with color",
        "start": {"dateTime": "2023-01-01T09:00:00+00:00"},
        "end": {"dateTime": "2023-01-01T10:00:00+00:00"},
        "location": "Test Location",
        "extendedProperties": extended_properties,
        "colorId": color.to_color_id(),
    }


def test_all_day_event_to_google_event():
    # Arrange
    service = Mock()
    calendar_id = "test_calendar_id"
    manager = GoogleCalendarManager(service=service, calendar_id=calendar_id)

    event = Event(
        start=arrow.get("2023-01-01T00:00:00+00:00"),
        end=arrow.get("2023-01-02T00:00:00+00:00"),
        title="All Day Event",
        is_all_day=True,
    )

    # Act
    google_event = manager._event_to_google_event(event, {})

    # Assert
    assert google_event["start"] == {"date": "2023-01-01"}
    assert google_event["end"] == {"date": "2023-01-02"}


def test_get_syncademic_marker():
    # Arrange
    service = Mock()
    calendar_id = "test_calendar_id"
    manager = GoogleCalendarManager(service=service, calendar_id=calendar_id)
    sync_profile_id = "test_sync_profile"

    # Act
    marker = manager._create_extended_properties(sync_profile_id)

    # Assert
    assert marker == {"private": {"syncademic": sync_profile_id}}


def test_create_events_successful():
    # Arrange
    service = Mock()
    batch = Mock()
    service.new_batch_http_request.return_value = batch
    calendar_id = "test_calendar_id"
    manager = GoogleCalendarManager(service=service, calendar_id=calendar_id)
    sync_profile_id = "test_sync_profile"

    event1 = Event(
        start=arrow.get("2023-01-01T09:00:00+00:00"),
        end=arrow.get("2023-01-01T10:00:00+00:00"),
        title="Event 1",
        description="Description 1",
        location="Location 1",
    )
    event2 = Event(
        start=arrow.get("2023-01-02T09:00:00+00:00"),
        end=arrow.get("2023-01-02T10:00:00+00:00"),
        title="Event 2",
        description="Description 2",
        location="Location 2",
    )
    events = [event1, event2]

    # Act
    manager.create_events(
        events=events,
        sync_profile_id=sync_profile_id,
    )

    # Assert
    service.new_batch_http_request.assert_called_once()
    assert batch.add.call_count == 2
    batch.execute.assert_called_once()


def test_create_events_in_batches():
    # Arrange
    service = Mock()
    batch_calls = []

    def new_batch_http_request():
        batch = Mock()
        batch_calls.append(batch)
        return batch

    service.new_batch_http_request.side_effect = new_batch_http_request

    calendar_id = "test_calendar_id"
    manager = GoogleCalendarManager(service=service, calendar_id=calendar_id)
    sync_profile_id = "test_sync_profile"

    n_events = 105
    batch_size = 50

    # Create more than 50 events to test batching
    events = [
        Event(
            start=arrow.get(f"2023-01-{(i % 31) + 1:02d}T09:00:00+00:00"),
            end=arrow.get(f"2023-01-{(i % 31) + 1:02d}T10:00:00+00:00"),
            title=f"Event {i + 1}",
            description=f"Description {i + 1}",
            location=f"Location {i + 1}",
        )
        for i in range(n_events)
    ]

    # Act
    manager.create_events(
        events=events,
        sync_profile_id=sync_profile_id,
        batch_size=batch_size,
    )

    # Assert
    assert service.new_batch_http_request.call_count == n_events // batch_size + 1
    total_add_calls = sum(batch.add.call_count for batch in batch_calls)
    assert total_add_calls == n_events
    total_execute_calls = sum(batch.execute.call_count for batch in batch_calls)
    assert total_execute_calls == n_events // batch_size + 1


def test_get_events_ids_from_sync_profile():
    # Arrange
    service = Mock()
    calendar_id = "test_calendar_id"
    manager = GoogleCalendarManager(service=service, calendar_id=calendar_id)
    sync_profile_id = "test_sync_profile"
    min_dt = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    # Mock the service.events().list().execute() chain
    events_list = [{"id": "event_id_1"}, {"id": "event_id_2"}]
    list_request = Mock()
    list_request.execute.return_value = {"items": events_list}
    service.events.return_value.list.return_value = list_request
    service.events.return_value.list_next.return_value = None  # To end the loop

    # Act
    event_ids = manager.get_events_ids_from_sync_profile(
        sync_profile_id=sync_profile_id,
        min_dt=min_dt,
    )

    # Assert
    service.events.return_value.list.assert_called_once_with(
        calendarId=calendar_id,
        privateExtendedProperty=f"syncademic={sync_profile_id}",
        singleEvents=True,
        orderBy="startTime",
        maxResults=1000,
        timeMin=min_dt.isoformat(),
    )
    assert event_ids == ["event_id_1", "event_id_2"]


def test_get_events_ids_from_sync_profile_multiple_pages():
    # Arrange
    service = Mock()
    calendar_id = "test_calendar_id"
    manager = GoogleCalendarManager(service=service, calendar_id=calendar_id)
    sync_profile_id = "test_sync_profile"

    # Mock the first page
    events_page_1 = {"items": [{"id": "event_id_1"}]}
    # Mock the second page
    events_page_2 = {"items": [{"id": "event_id_2"}]}

    request = Mock()
    request.execute.side_effect = [events_page_1, events_page_2]
    service.events.return_value.list.return_value = request
    service.events.return_value.list_next.side_effect = [request, None]

    # Act
    event_ids = manager.get_events_ids_from_sync_profile(
        sync_profile_id=sync_profile_id,
    )

    # Assert
    assert event_ids == ["event_id_1", "event_id_2"]


def test_delete_events_successful():
    # Arrange
    service = Mock()
    batch = Mock()
    service.new_batch_http_request.return_value = batch
    calendar_id = "test_calendar_id"
    manager = GoogleCalendarManager(service=service, calendar_id=calendar_id)

    event_ids = ["event_id_1", "event_id_2"]

    # Act
    manager.delete_events(event_ids)

    # Assert
    service.new_batch_http_request.assert_called_once()
    assert batch.add.call_count == 2
    batch.execute.assert_called_once()


def test_delete_events_in_batches():
    # Arrange
    service = Mock()
    batch_calls = []

    def new_batch_http_request():
        batch = Mock()
        batch_calls.append(batch)
        return batch

    service.new_batch_http_request.side_effect = new_batch_http_request

    calendar_id = "test_calendar_id"
    manager = GoogleCalendarManager(service=service, calendar_id=calendar_id)

    # Create more than 50 event IDs to test batching
    n_events = 105
    batch_size = 50

    event_ids = [f"event_id_{i}" for i in range(n_events)]

    # Act
    manager.delete_events(event_ids, batch_size=batch_size)

    # Assert
    assert service.new_batch_http_request.call_count == 3  # 105 events / 50 per batch
    total_add_calls = sum(batch.add.call_count for batch in batch_calls)
    assert total_add_calls == 105
    total_execute_calls = sum(batch.execute.call_count for batch in batch_calls)
    assert total_execute_calls == 3
