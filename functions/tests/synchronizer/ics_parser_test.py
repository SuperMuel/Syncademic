from typing import List
from src.shared.event import Event
from src.synchronizer.ics_parser import IcsParser
import unittest
import arrow


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


def build_ics(events: List[Event]):
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


class TestIcsParser(unittest.TestCase):
    def setUp(self):
        self.ics_parser = IcsParser()

    def test_parse(self):
        """Test parsing a valid ics string."""
        ics_str = build_ics([event1])
        events = self.ics_parser.parse(ics_str)
        self.assertEqual(events, [event1])

    def test_parse_empty_string_throws(self):
        """Test parsing an empty ics string."""
        ics_str = ""

        with self.assertRaises(Exception):
            self.ics_parser.parse(ics_str)

    def test_parse_no_events(self):
        """Test parsing an empty ics string."""
        ics_str = build_ics_outline("")
        events = self.ics_parser.parse(ics_str)
        self.assertEqual(events, [])

    def test_parse_invalid(self):
        """Test parsing an invalid ics string."""
        ics_str = "invalid"
        with self.assertRaises(Exception):
            self.ics_parser.parse(ics_str)

    def test_parse_multiple(self):
        """Test parsing multiple events."""
        ics_str = build_ics([event1, event2])
        events = self.ics_parser.parse(ics_str)

        self.assertTrue(events[0] == event1 or events[0] == event2)
        self.assertTrue(events[1] == event1 or events[1] == event2)
        self.assertNotEqual(events[0], events[1])

    def test_an_event_has_no_title(self):
        """Test that an event has no title."""
        ics_str = build_ics_outline(
            """BEGIN:VEVENT
DESCRIPTION:Description
LOCATION:Location
DTSTART:20230101T090000
DTEND:20230101T100000
END:VEVENT"""
        )
        events = self.ics_parser.parse(ics_str)
        self.assertEqual(events[0].title, "")

    def test_an_event_has_no_description(self):
        """Test that an event has no description."""
        ics_str = build_ics_outline(
            """BEGIN:VEVENT
SUMMARY:Title
LOCATION:Location
DTSTART:20230101T090000
DTEND:20230101T100000
END:VEVENT"""
        )
        events = self.ics_parser.parse(ics_str)
        self.assertEqual(events[0].description, "")

    def test_an_event_has_no_location(self):
        """Test that an event has no location."""
        ics_str = build_ics_outline(
            """BEGIN:VEVENT
SUMMARY:Title
DESCRIPTION:Description
DTSTART:20230101T090000
DTEND:20230101T100000
END:VEVENT"""
        )
        events = self.ics_parser.parse(ics_str)
        self.assertEqual(events[0].location, "")

    def test_an_event_has_no_start_throws(self):
        """Test that an event has no start."""
        ics_str = build_ics_outline(
            """BEGIN:VEVENT
SUMMARY:Title
DESCRIPTION:Description
LOCATION:Location
DTEND:20230101T100000
END:VEVENT"""
        )
        with self.assertRaises(Exception):
            self.ics_parser.parse(ics_str)

    def test_an_event_has_no_end_throws(self):
        """Test that an event has no end."""
        ics_str = build_ics_outline(
            """BEGIN:VEVENT
SUMMARY:Title
DESCRIPTION:Description
LOCATION:Location
DTSTART:20230101T090000
END:VEVENT"""
        )
        with self.assertRaises(Exception):
            self.ics_parser.parse(ics_str)

    def test_an_event_has_start_after_end_throws(self):
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
        with self.assertRaises(Exception):
            self.ics_parser.parse(ics_str)

    def test_an_event_has_start_equal_end_throws(self):
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
        with self.assertRaises(Exception):
            self.ics_parser.parse(ics_str)
