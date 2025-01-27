from datetime import datetime
from typing import Any

from functions.shared.event import Event
from functions.synchronizer.google_calendar_manager import (
    GoogleCalendarManager,
    ExtendedProperties,
)


class MockGoogleCalendarManager(GoogleCalendarManager):
    """An in-memory implementation of GoogleCalendarManager for testing purposes.

    This mock stores events in memory and simulates the behavior of the Google Calendar API
    without making actual API calls.
    """

    def __init__(self) -> None:
        # No need for service or calendar_id in mock
        super().__init__(service=None, calendar_id="mock-calendar")
        # Store events as {event_id: (event_dict, sync_profile_id)}
        self._events: dict[str, tuple[dict[str, Any], str]] = {}
        self._next_event_id = 1

    def create_events(
        self,
        events: list[Event],
        *,
        sync_profile_id: str,
        batch_size: int = 50,
    ) -> None:
        """Store events in memory with generated IDs."""
        for event in events:
            event_id = str(self._next_event_id)
            self._next_event_id += 1

            google_event = self._event_to_google_event(
                event,
                extended_properties=self._create_extended_properties(sync_profile_id),
            )

            self._events[event_id] = (google_event, sync_profile_id)

    def get_events_ids_from_sync_profile(
        self,
        *,
        sync_profile_id: str,
        min_dt: datetime | None = None,
        limit: int | None = 1000,
    ) -> list[str]:
        """Retrieve event IDs filtered by sync profile and optional minimum datetime."""
        matching_ids = []

        for event_id, (event_dict, stored_profile_id) in self._events.items():
            if stored_profile_id != sync_profile_id:
                continue

            if min_dt is not None:
                event_end = event_dict["end"]["dateTime"]
                if event_end <= min_dt.isoformat():
                    continue

            matching_ids.append(event_id)

            if limit and len(matching_ids) >= limit:
                break

        return matching_ids

    def delete_events(
        self,
        ids: list[str],
        *,
        batch_size: int = 50,
    ) -> None:
        """Remove events from in-memory storage."""
        for event_id in ids:
            self._events.pop(event_id, None)

    def get_all_events(self) -> dict[str, tuple[dict[str, Any], str]]:
        """Helper method for testing - returns all stored events.

        Returns:
            Dictionary mapping event IDs to tuples of (event_dict, sync_profile_id)
        """
        return self._events.copy()
