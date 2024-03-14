from synchronizer.synchronizer import SynchronizationResult, perform_synchronization
import unittest
from unittest.mock import MagicMock, patch
from synchronizer.ics_source import UrlIcsSource
from synchronizer.ics_parser import IcsParser


class TestSynchronizer(unittest.TestCase):

    def setUp(self):
        self.syncConfigId = "syncConfigId"
        self.icsSourceUrl = "https://example.com/calendar.ics"
        self.targetCalendarId = "targetCalendarId"
        self.service = MagicMock()

    @patch("synchronizer.synchronizer.UrlIcsSource")
    @patch("synchronizer.synchronizer.IcsParser")
    @patch("synchronizer.synchronizer.GoogleCalendarManager")
    def test_perform_synchronization_success(
        self, mock_manager, mock_parser, mock_source
    ):
        # Setup mocks
        mock_source.return_value.get_ics_string.return_value = "ICS_STRING"
        mock_event = MagicMock()
        mock_parser.return_value.parse.return_value = [mock_event]

        mock_service = MagicMock()
        mock_manager_instance = mock_manager.return_value
        mock_manager_instance.create_events.return_value = None

        # Execute the method under test
        result = perform_synchronization(
            syncConfigId="test_sync_id",
            icsSourceUrl="http://example.com/calendar.ics",
            targetCalendarId="target_calendar_id",
            service=mock_service,
        )

        # Assertions
        self.assertIsInstance(result, SynchronizationResult)
        self.assertTrue(result.success)

        mock_source.assert_called_once_with("http://example.com/calendar.ics")
        mock_parser().parse.assert_called_once_with("ICS_STRING")
        mock_manager_instance.create_events.assert_called_once()


if __name__ == "__main__":
    unittest.main()
