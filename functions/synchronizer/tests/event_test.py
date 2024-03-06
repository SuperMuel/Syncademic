import arrow
from synchronizer.event import Event
import unittest


class TestEvent(unittest.TestCase):

    def setUp(self):
        self.start = arrow.get("2023-01-01T09:00:00")
        self.end = arrow.get("2023-01-01T10:00:00")
        self.title = "Meeting"
        self.description = "Discuss project"
        self.location = "Office"
        self.extended_properties = {"attendees": 10}

    def test_event_creation_successful(self):
        """Test successful creation of an Event instance."""
        event = Event(
            start=self.start,
            end=self.end,
            title=self.title,
            description=self.description,
            location=self.location,
            extended_properties=self.extended_properties,
        )
        self.assertEqual(event.start, self.start)
        self.assertEqual(event.end, self.end)
        self.assertEqual(event.title, self.title)
        self.assertEqual(event.description, self.description)
        self.assertEqual(event.location, self.location)
        self.assertEqual(event.extended_properties, self.extended_properties)

    def test_event_creation_without_start_end_raises_value_error(self):
        """Test that creating an Event without start or end raises ValueError."""
        with self.assertRaises(ValueError):
            Event(start=None, end=self.end)  # type: ignore
        with self.assertRaises(ValueError):
            Event(start=self.start, end=None)  # type: ignore

    def test_event_creation_with_end_before_start_raises_value_error(self):
        """Test that creating an Event with the end before the start raises ValueError."""
        with self.assertRaises(ValueError):
            Event(start=self.end, end=self.start)

    def test_event_creation_with_end_equal_start_raises_value_error(self):
        """Test that creating an Event with the end equal to the start raises ValueError."""
        with self.assertRaises(ValueError):
            Event(start=self.start, end=self.start)

    def test_equals(self):
        """Test that two events are equal."""
        event1 = Event(
            start=self.start,
            end=self.end,
            title=self.title,
            description=self.description,
            location=self.location,
            extended_properties={"attendees": 10, "deep": {"nested": "property"}},
        )
        event2 = Event(
            start=self.start,
            end=self.end,
            title=self.title,
            description=self.description,
            location=self.location,
            extended_properties={"attendees": 10, "deep": {"nested": "property"}},
        )
        self.assertEqual(event1, event2)

    def test_not_equals(self):
        """Test that two events are not equal."""
        event1 = Event(
            start=self.start,
            end=self.end,
            title=self.title,
            description=self.description,
            location=self.location,
        )
        event2 = Event(
            start=self.start,
            end=self.end,
            title=self.title + "42",
            description=self.description,
            location=self.location,
        )
        self.assertNotEqual(event1, event2)

    def test_not_equals_different_extended_properties(self):
        """Test that two events are not equal."""
        event1 = Event(
            start=self.start,
            end=self.end,
            title=self.title,
            description=self.description,
            location=self.location,
            extended_properties=self.extended_properties,
        )
        event2 = Event(
            start=self.start,
            end=self.end,
            title=self.title,
            description=self.description,
            location=self.location,
            extended_properties={"attendees": 11},
        )
        self.assertNotEqual(event1, event2)


if __name__ == "__main__":
    unittest.main()
