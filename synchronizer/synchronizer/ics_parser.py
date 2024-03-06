from typing import List
from event import Event
import ics


class IcsParser:
    def __init__(self):
        pass

    def parse(self, ics_str: str) -> List[Event]:
        calendar = ics.Calendar(ics_str)
        return [
            Event(
                title=event.name,
                description=event.description or "",
                start=event.begin,
                end=event.end,
                location=event.location or "",
            )
            for event in calendar.events
        ]
