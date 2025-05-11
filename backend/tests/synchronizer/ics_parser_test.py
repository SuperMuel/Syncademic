from typing import List

import arrow
import pytest

from backend.services.exceptions.ics import IcsParsingError
from backend.shared.event import Event
from backend.synchronizer.ics_parser import IcsParser, RecurringEventError


def build_ics_outline(inside: str):
    return f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Syncademic Inc//Syncademic//EN
{inside}
END:VCALENDAR"""


def event_to_ics(event: Event):
    return f"""BEGIN:VEVENT
SUMMARY:{event.title}
DESCRIPTION:{event.description}
DTSTART:{event.start.format("YYYYMMDDTHHmmss")}
DTEND:{event.end.format("YYYYMMDDTHHmmss")}
LOCATION:{event.location}
END:VEVENT"""


def build_ics(events: list[Event]) -> str:
    return build_ics_outline("\n".join([event_to_ics(event) for event in events]))


event1 = Event(
    start=arrow.get("2023-01-01T09:00:00"),
    end=arrow.get("2023-01-01T10:00:00"),
    title="Meeting",
    description="Discuss project",
    location="Office",
)

event2 = Event(
    start=arrow.get("2023-01-01T09:00:00"),
    end=arrow.get("2023-01-01T10:00:00"),
    title="Meeting2",
    description="Discuss project 2",
    location="Office2",
)


@pytest.fixture
def ics_parser() -> IcsParser:
    return IcsParser()


def test_parse(ics_parser: IcsParser):
    """Test parsing a valid ics string."""
    ics_str = build_ics([event1])
    events = ics_parser.try_parse(ics_str)
    assert events == [event1]


def test_parse_empty_string_throws(ics_parser: IcsParser):
    """Test parsing an empty ics string."""
    ics_str = ""

    error = ics_parser.try_parse(ics_str)
    assert isinstance(error, IcsParsingError)


def test_parse_no_events(ics_parser: IcsParser):
    """Test parsing an empty ics string."""
    ics_str = build_ics_outline("")
    events = ics_parser.try_parse(ics_str)
    assert events == []


def test_parse_invalid(ics_parser: IcsParser):
    """Test parsing an invalid ics string."""
    ics_str = "invalid"
    error = ics_parser.try_parse(ics_str)
    assert isinstance(error, IcsParsingError)


def test_parse_multiple(ics_parser: IcsParser):
    """Test parsing multiple events."""
    ics_str = build_ics([event1, event2])
    events = ics_parser.try_parse(ics_str)
    assert isinstance(events, list)
    assert len(events) == 2

    assert events[0] == event1 or events[0] == event2
    assert events[1] == event1 or events[1] == event2
    assert events[0] != events[1]


def test_an_event_has_no_title(ics_parser: IcsParser):
    """Test that an event has no title."""
    ics_str = build_ics_outline(
        """BEGIN:VEVENT
DESCRIPTION:Description
LOCATION:Location
DTSTART:20230101T090000
DTEND:20230101T100000
END:VEVENT"""
    )
    events = ics_parser.try_parse(ics_str)
    assert isinstance(events, list)
    assert events[0].title == ""


def test_an_event_has_no_description(ics_parser: IcsParser):
    """Test that an event has no description."""
    ics_str = build_ics_outline(
        """BEGIN:VEVENT
SUMMARY:Title
LOCATION:Location
DTSTART:20230101T090000
DTEND:20230101T100000
END:VEVENT"""
    )
    events = ics_parser.try_parse(ics_str)
    assert isinstance(events, list)
    assert events[0].description == ""


def test_an_event_has_no_location(ics_parser: IcsParser):
    """Test that an event has no location."""
    ics_str = build_ics_outline(
        """BEGIN:VEVENT
SUMMARY:Title
DESCRIPTION:Description
DTSTART:20230101T090000
DTEND:20230101T100000
END:VEVENT"""
    )
    events = ics_parser.try_parse(ics_str)
    assert isinstance(events, list)
    assert events[0].location == ""


def test_an_event_has_no_start_throws(ics_parser: IcsParser):
    """Test that an event has no start."""
    ics_str = build_ics_outline(
        """BEGIN:VEVENT
SUMMARY:Title
DESCRIPTION:Description
LOCATION:Location
DTEND:20230101T100000
END:VEVENT"""
    )
    error = ics_parser.try_parse(ics_str)
    assert isinstance(error, IcsParsingError)


def test_an_event_has_no_end_throws(ics_parser: IcsParser):
    """Test that an event has no end."""
    ics_str = build_ics_outline(
        """BEGIN:VEVENT
SUMMARY:Title
DESCRIPTION:Description
LOCATION:Location
DTSTART:20230101T090000
END:VEVENT"""
    )
    error = ics_parser.try_parse(ics_str)
    assert isinstance(error, IcsParsingError)


def test_an_event_has_start_after_end_throws(ics_parser: IcsParser):
    """Test that an event has start after end."""
    ics_str = build_ics_outline(
        """BEGIN:VEVENT 
SUMMARY:Title
DESCRIPTION:Description
LOCATION:Location
DTSTART:20230101T100000
DTEND:20230101T090000
END:VEVENT"""
    )
    error = ics_parser.try_parse(ics_str)
    assert isinstance(error, IcsParsingError)


def test_an_event_has_start_equal_end_throws(ics_parser: IcsParser):
    """Test that an event has start equal end."""
    ics_str = build_ics_outline(
        """BEGIN:VEVENT
SUMMARY:Title
DESCRIPTION:Description
LOCATION:Location
DTSTART:20230101T090000
DTEND:20230101T090000
END:VEVENT"""
    )
    error = ics_parser.try_parse(ics_str)
    assert isinstance(error, IcsParsingError)


def test_recurring_event_with_rrule_throws(ics_parser: IcsParser):
    """Test that a recurring event with RRULE raises an error. We do not support recurring events yet."""
    ics_str = build_ics_outline(
        """BEGIN:VEVENT
SUMMARY:Recurring Event
DTSTART:20230101T090000
DTEND:20230101T100000
RRULE:FREQ=DAILY;COUNT=5
END:VEVENT"""
    )
    # with pytest.raises(RecurringEventError):
    #     ics_parser.parse(ics_str)

    error = ics_parser.try_parse(ics_str)
    assert isinstance(error, RecurringEventError)


def test_recurring_event_with_rdate_throws(ics_parser: IcsParser):
    """Test that a recurring event with RDATE raises an error. We do not support recurring events yet."""
    ics_str = build_ics_outline(
        """BEGIN:VEVENT
SUMMARY:Recurring Event
DTSTART:20230101T090000
DTEND:20230101T100000
RDATE:20230102T090000,20230103T090000
END:VEVENT"""
    )
    error = ics_parser.try_parse(ics_str)
    assert isinstance(error, RecurringEventError)


def test_recurring_event_with_exdate_throws(ics_parser: IcsParser):
    """Test that a recurring event with EXDATE raises an error. We do not support recurring events yet."""
    ics_str = build_ics_outline(
        """BEGIN:VEVENT
SUMMARY:Recurring Event
DTSTART:20230101T090000
DTEND:20230101T100000
EXDATE:20230102T090000
END:VEVENT"""
    )
    error = ics_parser.try_parse(ics_str)
    assert isinstance(error, RecurringEventError)


def test_empty_ics_string(ics_parser: IcsParser):
    error = ics_parser.try_parse("")
    assert isinstance(error, IcsParsingError)


def test_all_day_event(ics_parser: IcsParser):
    """Test parsing an all-day event with VALUE=DATE format."""
    ics_str = build_ics_outline(
        """BEGIN:VEVENT
DTSTAMP:20250318T060707Z
UID:MockUID
DTSTART;VALUE=DATE:20250609
DTEND;VALUE=DATE:20250610
SUMMARY;LANGUAGE=fr:This is an All day event
END:VEVENT"""
    )
    events = ics_parser.try_parse(ics_str)

    assert isinstance(events, list)
    assert len(events) == 1

    event = events[0]
    assert event.title == "This is an All day event"
    assert event.start.format("YYYY-MM-DD") == "2025-06-09"
    assert event.end.format("YYYY-MM-DD") == "2025-06-10"
    assert event.is_all_day
