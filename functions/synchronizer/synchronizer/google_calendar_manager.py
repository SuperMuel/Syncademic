from typing import List, TypeAlias, Dict
from .event import Event
from itertools import islice

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

        return {
            "summary": event.title,
            "description": event.description,
            "start": {"dateTime": start_time_rfc3339},
            "end": {"dateTime": end_time_rfc3339},
            "location": event.location,
            "extendedProperties": extended_properties,
        }

    def _get_syncademic_marker(self, sync_profile_id) -> ExtendedProperties:
        return {"private": {"syncademic": sync_profile_id}}

    def create_events(self, events: List[Event], sync_profile_id: str) -> None:
        for sublist in batched(events, 50):  # TODO : check maximum batch size
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

    def delete_events(self, events: List[Event], sync_profile_id: str) -> None:
        # TODO : check that the events we delete are marked with syncademic
        # to prevent deleting user events
        pass
