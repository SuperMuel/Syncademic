from datetime import datetime
from typing import List, Optional, TypeAlias, Dict
from itertools import islice
import pytz
from firebase_functions import logger
from src.shared.event import Event

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
            body["colorId"] = event.color.value

        return body

    def _get_syncademic_marker(self, sync_profile_id) -> ExtendedProperties:
        assert sync_profile_id
        return {"private": {"syncademic": sync_profile_id}}

    def create_events(self, events: List[Event], sync_profile_id: str) -> None:
        logger.info(f"Creating {len(events)} events.")

        if len(events) > 1000:
            raise Exception(f"Too many events. ({len(events)})")

        for i, sublist in enumerate(
            batched(events, 50)
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
        if not sync_profile_id:
            raise ValueError(f"{sync_profile_id=} is not valid")

        events_as_dict = []

        request = self.service.events().list(
            calendarId=self.calendar_id,
            privateExtendedProperty=f"syncademic={sync_profile_id}",
            singleEvents=True,
            orderBy="startTime",
            maxResults=limit,
            timeMin=min_dt.astimezone(pytz.utc).isoformat() if min_dt else None,
        )

        while request:  # TODO : Add a limit to avoid infinite loops
            response = request.execute()
            events_as_dict.extend(response.get("items", []))
            request = self.service.events().list_next(request, response)

        return [event["id"] for event in events_as_dict]

    def delete_events(self, ids: List[str]) -> None:
        logger.info(f"Deleting {len(ids)} events.")
        for sublist in batched(ids, 50):
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
