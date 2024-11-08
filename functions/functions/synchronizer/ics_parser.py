from typing import List

from functions.shared.event import Event
import ics


class RecurringEventError(Exception):
    """Custom exception raised when a recurring event is detected because we don't support them yet."""

    pass


def check_for_recurring_event(event) -> None:
    """
    Check if an event contains recurrence properties and raise RecurringEventError if found.

    Args:
        event: The ICS event to check

    Raises:
        RecurringEventError: If the event contains any recurrence properties
    """
    extra_names: list[str] = [extra.name for extra in event.extra]
    assert all(isinstance(name, str) for name in extra_names)

    if any(
        extra_name.startswith(prop)
        for extra_name in extra_names
        for prop in ["RRULE", "RDATE", "EXDATE"]
    ):
        raise RecurringEventError(
            f"Recurring event detected: {event.name=}, {extra_names=}. We do not support recurring events yet."
        )


class IcsParser:
    def __init__(self):
        pass

    def parse(self, ics_str: str) -> List[Event]:
        calendar = ics.Calendar(ics_str)
        events = []
        for event in calendar.events:
            check_for_recurring_event(event)

            # Append non-recurring events to the list
            events.append(
                Event(
                    title=event.name or "",
                    description=event.description or "",
                    start=event.begin,
                    end=event.end,
                    location=event.location or "",
                )
            )
        return events
