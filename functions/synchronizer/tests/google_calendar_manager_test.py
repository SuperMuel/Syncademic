import unittest
from unittest.mock import Mock, patch
from synchronizer.google_calendar_manager import GoogleCalendarManager
from synchronizer.event import Event
import arrow


class TestGoogleCalendarManager(unittest.TestCase):
    def setUp(self):
        self.service_mock = Mock()
        self.calendar_id = "test_calendar_id"
        self.sync_profile_id = "sync_profile_123"
        self.google_calendar_manager = GoogleCalendarManager(
            self.service_mock, self.calendar_id
        )

        # Mock event
        self.event = Event(
            start=arrow.get("2023-01-01T09:00:00+00:00"),
            end=arrow.get("2023-01-01T10:00:00+00:00"),
            title="Test Event",
            description="This is a test event.",
            location="Test Location",
        )

    @patch("synchronizer.google_calendar_manager.batched")
    def test_create_events(self, mock_batched):
        # Prepare the mock for batched function
        mock_batched.return_value = [
            [self.event]
        ]  # Simulate a single batch with one event

        # Mock batch request
        batch_request_mock = Mock()
        self.service_mock.new_batch_http_request.return_value = batch_request_mock

        # Execute the method under test
        self.google_calendar_manager.create_events([self.event], self.sync_profile_id)

        # Assertions to verify correct behavior
        self.service_mock.new_batch_http_request.assert_called_once()
        batch_request_mock.add.assert_called()
        batch_request_mock.execute.assert_called_once()

        # Check if the event added to the batch request is correctly formatted
        google_event = self.google_calendar_manager.event_to_google_event(
            self.event,
            self.google_calendar_manager._get_syncademic_marker(self.sync_profile_id),
        )
        batch_request_mock.add.assert_called_with(
            self.service_mock.events().insert(
                calendarId=self.calendar_id,
                body=google_event,
            )
        )


if __name__ == "__main__":
    unittest.main()
