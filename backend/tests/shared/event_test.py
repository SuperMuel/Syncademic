import arrow
import pytest
from functions.shared.event import Event
from functions.shared.google_calendar_colors import GoogleEventColor

start = arrow.get("2024-03-01T10:00:00")
end = arrow.get("2024-03-01T12:00:00")
title = "Test Event"
description = "A test event"
location = "Test Location"


def test_event_initialization():
    event = Event(
        start=start,
        end=end,
        title="Test Event",
        description="A test event",
        location="Test Location",
    )

    assert event.start == start
    assert event.end == end
    assert event.title == "Test Event"
    assert event.description == "A test event"
    assert event.location == "Test Location"
    assert event.color is None  # default is None


def test_event_start_after_end():
    start = arrow.get("2024-03-01T12:00:00")
    end = arrow.get("2024-03-01T10:00:00")

    with pytest.raises(ValueError, match="Start date must be before end date"):
        Event(start=start, end=end, title="Invalid Event")


def test_event_start_equal_end():
    start = arrow.get("2024-03-01T12:00:00")
    end = arrow.get("2024-03-01T12:00:00")

    with pytest.raises(ValueError, match="Start date must be before end date"):
        Event(start=start, end=end, title="Invalid Event")


def test_event_missing_dates():
    with pytest.raises(ValueError, match="Both start and end dates must be provided"):
        Event(
            start=None,  # type: ignore
            end=arrow.get("2024-03-01T12:00:00"),
        )

    with pytest.raises(ValueError, match="Both start and end dates must be provided"):
        Event(
            start=arrow.get("2024-03-01T10:00:00"),
            end=None,  # type: ignore
        )


def test_event_missing_title():
    with pytest.raises(ValueError, match="Title must be provided"):
        Event(
            title=None,  # type: ignore
            start=start,
            end=end,
        )


def test_event_with_color():
    color = GoogleEventColor.TOMATO

    event = Event(start=start, end=end, title="Colored Event", color=color)

    assert event.color == color


def test_equals():
    event1 = Event(
        start=start,
        end=end,
        title=title,
        description=description,
        location=location,
    )
    event2 = Event(
        start=start,
        end=end,
        title=title,
        description=description,
        location=location,
    )
    assert event1 == event2


def test_not_equals():
    event1 = Event(
        start=start,
        end=end,
        title=title,
        description=description,
        location=location,
    )
    event2 = Event(
        start=start,
        end=end,
        title=title + "42",
        description=description,
        location=location,
    )
    assert event1 != event2


def test_hash():
    event1 = Event(
        start=start,
        end=end,
        title=title,
        description=description,
        location=location,
    )
    event2 = Event(
        start=start,
        end=end,
        title=title,
        description=description,
        location=location,
    )
    assert hash(event1) == hash(event2)


def test_duplicates_can_be_removed_with_set():
    event1 = Event(
        start=start,
        end=end,
        title=title,
        description=description,
        location=location,
    )
    event2 = Event(
        start=start,
        end=end,
        title=title,
        description=description,
        location=location,
    )
    assert len({event1, event2}) == 1
