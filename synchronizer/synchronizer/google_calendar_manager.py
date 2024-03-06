from itertools import batched
from typing import Any, List
from event import Event


class GoogleCalendarManager:
    def __init__(self, service, calendar_id: str):
        self.service = service
        self.calendar_id = calendar_id

    def event_to_google_event(self, event: Event) -> dict:
        # Format the start and end times to RFC 3339
        start_time_rfc3339 = event.start.format("YYYY-MM-DDTHH:mm:ssZZ")
        end_time_rfc3339 = event.end.format("YYYY-MM-DDTHH:mm:ssZZ")

        return {
            "summary": event.title,
            "description": event.description,
            "start": {"dateTime": start_time_rfc3339},
            "end": {"dateTime": end_time_rfc3339},
            "location": event.location,
            "extendedProperties": event.extended_properties,
        }

    def create_events(self, events: List[Event]) -> None:
        batch = self.service.new_batch_http_request()
        for sublist in batched(events, 50):  # TODO : check maximum batch size
            for event in sublist:
                batch.add(
                    self.service.events().insert(
                        calendarId=self.calendar_id,
                        body=self.event_to_google_event(event),
                    )
                )
            batch.execute()

    def delete_events(self, events: List[Event]) -> None:
        # TODO : check that the events we delete are marked with syncademia
        # to prevent deleting user events
        pass
