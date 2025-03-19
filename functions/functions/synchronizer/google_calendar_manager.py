from datetime import datetime
from itertools import islice
from typing import Any, Dict, Iterable, List, Optional, TypeAlias

import googleapiclient
import pytz
from firebase_functions import logger
from googleapiclient.errors import HttpError

from functions.shared.event import Event

ExtendedProperties: TypeAlias = dict[str, Any]


def batched(iterable: Iterable, batch_size: int) -> Iterable[list]:
    """
    Batch an iterable into chunks of a given size.
    """
    iterator = iter(iterable)
    while True:
        batch = list(islice(iterator, batch_size))
        if not batch:
            break
        yield batch


class GoogleCalendarManager:
    """Create, retrieve, and delete events in Google Calendar,
    with support for batch operations and extended properties for sync tracking.

    The manager handles:
    - Converting our Event objects to Google Calendar event format
    - Batch creation of events
    - Retrieving event IDs based on sync profile
    - Batch deletion of events

    All methods that interact with the Google Calendar API require a service object
    (googleapiclient.discovery.Resource) and a calendar_id.
    """

    def __init__(self, service: Any, calendar_id: str) -> None:
        self._service = service
        self._calendar_id = calendar_id

    @staticmethod
    def _event_to_google_event(
        event: Event, extended_properties: ExtendedProperties
    ) -> dict:
        if event.is_all_day:
            start = {"date": event.start.strftime("%Y-%m-%d")}
            end = {"date": event.end.strftime("%Y-%m-%d")}
        else:
            # Format the start and end times to RFC 3339
            start_time_rfc3339 = event.start.format("YYYY-MM-DDTHH:mm:ssZZ")
            end_time_rfc3339 = event.end.format("YYYY-MM-DDTHH:mm:ssZZ")

            start = {"dateTime": start_time_rfc3339}
            end = {"dateTime": end_time_rfc3339}

        body = {
            "summary": event.title,
            "description": event.description,
            "start": start,
            "end": end,
            "location": event.location,
            "extendedProperties": extended_properties,
        }

        if event.color:
            body["colorId"] = event.color.to_color_id()

        return body

    @staticmethod
    def _create_extended_properties(sync_profile_id: str) -> ExtendedProperties:
        if not sync_profile_id:
            raise ValueError(f"{sync_profile_id=} is not valid")
        return {"private": {"syncademic": sync_profile_id}}

    def create_events(
        self,
        events: list[Event],
        *,
        sync_profile_id: str,
        batch_size: int = 50,
    ) -> None:
        """Create multiple events in Google Calendar using batch requests.

        This method creates events in batches to optimize API usage. Each event is tagged
        with a sync profile ID in its extended properties for tracking purposes.

        Args:
            events: List of Event objects to create in Google Calendar.
            sync_profile_id: Identifier used to tag and track synced events to their sync profile.
            batch_size: Number of events to process in each batch request. Defaults to 50.
        """
        if len(events) > 10000:  # TODO : make this configurable
            raise ValueError(f"Too many events to create ({len(events)})")

        logger.info(f"Creating {len(events)} events.")

        for i, sublist in enumerate(
            batched(events, batch_size)
        ):  # TODO : check maximum batch size
            batch = self._service.new_batch_http_request()
            for event in sublist:
                google_event = self._event_to_google_event(
                    event,
                    extended_properties=self._create_extended_properties(
                        sync_profile_id
                    ),
                )
                batch.add(
                    self._service.events().insert(
                        calendarId=self._calendar_id,
                        body=google_event,
                    )
                )
            batch.execute()
            logger.info(f"Inserted {i * 50 + len(sublist)}/{len(events)} events.")

    def get_events_ids_from_sync_profile(
        self,
        *,
        sync_profile_id: str,
        min_dt: datetime | None = None,
        limit: int | None = 1000,
    ) -> list[str]:
        """Get the ids of the events associated with the sync_profile_id.

        Uses the privateExtendedProperty to filter the events.

        Args:
            sync_profile_id (str): The sync_profile_id to filter the events
            min_dt (datetime | None): The lower bound (exclusive) for an event's end time to filter by. Defaults to None.
            limit (int | None): The maximum number of events to return. Defaults to 1000.
        """
        if not sync_profile_id:
            raise ValueError(f"{sync_profile_id=} is not valid")

        events_as_dict = []

        request = self._service.events().list(
            calendarId=self._calendar_id,
            privateExtendedProperty=f"syncademic={sync_profile_id}",
            singleEvents=True,
            orderBy="startTime",
            maxResults=limit,
            # Lower bound (exclusive) for an event's end time to filter by. Optional.
            # The default is not to filter by end time. Must be an RFC3339 timestamp
            # with mandatory time zone offset, for example, 2011-06-03T10:00:00-07:00,
            #  2011-06-03T10:00:00Z. Milliseconds may be provided but are ignored.
            # If timeMax is set, timeMin must be smaller than timeMax.
            timeMin=min_dt.astimezone(pytz.utc).isoformat() if min_dt else None,
        )

        while request:
            response = request.execute()
            events_as_dict.extend(response.get("items", []))
            request = self._service.events().list_next(request, response)

        # TODO : assert here that the API respected timeMin

        return [event["id"] for event in events_as_dict]

    def delete_events(
        self,
        ids: list[str],
        *,
        batch_size: int = 50,
    ) -> None:
        """
        Delete events from the calendar by their ids.
        """
        logger.info(f"Deleting {len(ids)} events.")

        for i, sublist in enumerate(batched(ids, batch_size)):
            batch = self._service.new_batch_http_request()
            for id in sublist:
                batch.add(
                    self._service.events().delete(
                        calendarId=self._calendar_id,
                        eventId=id,
                    )
                )
            batch.execute()
            logger.info(f"Deleted {i * batch_size + len(sublist)}/{len(ids)} events.")

    def check_calendar_exists(self) -> bool:
        """
        Check if the calendar exists.

        Returns:
            bool: True if calendar exists, False otherwise

        Raises: All exception occuring except HttpError 404
        """

        try:
            self._service.calendars().get(calendarId=self._calendar_id).execute()
            return True
        except HttpError as e:
            if e.status_code == 404:
                logger.info(f"Calendar {self._calendar_id} not found")
                return False
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error checking calendar: {e.__class__.__name__}: {e}"
            )
            raise


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

    def get_all_events(self, *, sync_profile_id: str) -> list[dict[str, Any]]:
        """Helper method for testing - returns all stored events.

        Args:
            sync_profile_id (str): The sync_profile_id to filter the events

        Returns:
            List of events associated with the sync_profile_id
        """
        events = []
        for event_dict, stored_profile_id in self._events.values():
            if stored_profile_id == sync_profile_id:
                events.append(event_dict)
        return events

    def get_all_events_with_ids(
        self, *, sync_profile_id: str
    ) -> dict[str, dict[str, Any]]:
        """Helper method for testing - returns all stored events with their IDs.

        Args:
            sync_profile_id (str): The sync_profile_id to filter the events

        Returns:
            Dictionary mapping event IDs to their event data for the given sync_profile_id
        """
        events = {}
        for event_id, (event_dict, stored_profile_id) in self._events.items():
            if stored_profile_id == sync_profile_id:
                events[event_id] = event_dict
        return events
