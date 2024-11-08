from datetime import datetime
from typing import List, Optional, TypeAlias, Dict
from itertools import islice
import pytz
from firebase_functions import logger
from functions.shared.event import Event

ExtendedProperties: TypeAlias = Dict


def batched(iterable, batch_size):
    iterator = iter(iterable)
    while True:
        batch = list(islice(iterator, batch_size))
        if not batch:
            break
        yield batch


class GoogleCalendarManager:
    def __init__(self, service, calendar_id: str):
        self.service = service
        self.calendar_id = calendar_id

    def event_to_google_event(
        self, event: Event, extended_properties: ExtendedProperties
    ) -> dict:
        # Format the start and end times to RFC 3339
        start_time_rfc3339 = event.start.format("YYYY-MM-DDTHH:mm:ssZZ")
        end_time_rfc3339 = event.end.format("YYYY-MM-DDTHH:mm:ssZZ")

        body = {
            "summary": event.title,
            "description": event.description,
            "start": {"dateTime": start_time_rfc3339},
            "end": {"dateTime": end_time_rfc3339},
            "location": event.location,
            "extendedProperties": extended_properties,
        }

        if event.color:
            body["colorId"] = event.color.to_color_id()

        return body

    def _get_syncademic_marker(self, sync_profile_id) -> ExtendedProperties:
        assert sync_profile_id
        return {"private": {"syncademic": sync_profile_id}}

    def create_events(
        self, events: List[Event], sync_profile_id: str, batch_size: int = 50
    ) -> None:
        logger.info(f"Creating {len(events)} events.")

        if len(events) > 1000:
            raise Exception(f"Too many events. ({len(events)})")

        for i, sublist in enumerate(
            batched(events, batch_size)
        ):  # TODO : check maximum batch size
            batch = self.service.new_batch_http_request()
            for event in sublist:
                google_event = self.event_to_google_event(
                    event,
                    self._get_syncademic_marker(sync_profile_id),
                )
                batch.add(
                    self.service.events().insert(
                        calendarId=self.calendar_id,
                        body=google_event,
                    )
                )
            batch.execute()
            logger.info(f"Inserted {i * 50 + len(sublist)}/{len(events)} events.")

    def get_events_ids_from_sync_profile(
        self,
        sync_profile_id: str,
        min_dt: Optional[datetime] = None,
        limit: Optional[int] = 1000,
    ) -> List[str]:
        """Get the ids of the events associated with the sync_profile_id.

        Uses the privateExtendedProperty to filter the events.

        Args:
            sync_profile_id (str): The sync_profile_id to filter the events
            min_dt (Optional[datetime], optional): The lower bound (exclusive) for an event's end time to filter by. Defaults to None.
            limit (Optional[int], optional): The maximum number of events to return. Defaults to 1000.
        """
        if not sync_profile_id:
            raise ValueError(f"{sync_profile_id=} is not valid")

        events_as_dict = []

        request = self.service.events().list(
            calendarId=self.calendar_id,
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
            request = self.service.events().list_next(request, response)

        # TODO : assert here that the API respected timeMin

        return [event["id"] for event in events_as_dict]

    def delete_events(
        self,
        ids: list[str],
        batch_size: int = 50,
    ) -> None:
        logger.info(f"Deleting {len(ids)} events.")
        for sublist in batched(ids, batch_size):
            batch = self.service.new_batch_http_request()
            for id in sublist:
                batch.add(
                    self.service.events().delete(
                        calendarId=self.calendar_id,
                        eventId=id,
                    )
                )
            batch.execute()

    def test_authorization(self) -> None:
        logger.info("Testing authorization.")
        self.service.calendarList().list().execute(num_retries=3)
