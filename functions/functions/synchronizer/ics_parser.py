import logging
from typing import List

from functions.services.exceptions.ics import (
    IcsParsingError,
    RecurringEventError,
)
from functions.shared.event import Event
import ics

logger = logging.getLogger(__name__)


def _is_recurring_event(event: ics.Event) -> bool:
    """
    Check if an event contains recurrence properties and raise RecurringEventError if found.

    Args:
        event: The ICS event to check

    Returns:
        bool: True if the event is recurring, False otherwise
    """
    extra_names: list[str] = [extra.name for extra in event.extra]
    assert all(isinstance(name, str) for name in extra_names)

    recurring_props = ["RRULE", "RDATE", "EXDATE"]
    return any(
        extra_name.startswith(prop)
        for extra_name in extra_names
        for prop in recurring_props
    )


class IcsParser:
    """
    Parser for ICS (iCalendar) format strings into Event objects.

    This class handles the parsing of ICS calendar data, performing validation
    and conversion of calendar events into the internal Event model.

    Example:
        ```python
        parser = IcsParser()
        try:
            events = parser.try_parse(ics_string)
            if isinstance(events, IcsParsingError):
                print(f"Failed to parse: {events}")
            else:
                for event in events:
                    print(f"Parsed event: {event.title}")
        ```
    """

    def __init__(self):
        pass

    def try_parse(self, ics_str: str) -> list[Event] | IcsParsingError:
        """
        Attempt to parse an ICS string into a list of Event objects.

        This method performs several steps:
        1. Validates the input string is not empty
        2. Parses the ICS string into a calendar object
        3. Checks each event for unsupported recurring event properties
        4. Converts valid events into the internal Event model

        Args:
            ics_str: Raw ICS format string to parse

        Returns:
            Either a list of successfully parsed Event objects or an IcsParsingError
            if parsing fails

        Raises:
            IcsParsingError: If the input string is empty
            RecurringEventError: If any event contains recurrence rules (the exception is itself an IcsParsingError)
        """
        if not ics_str.strip():
            return IcsParsingError("Empty ICS string")

        try:
            calendar = ics.Calendar(ics_str)
        except Exception as e:
            logger.error(f"Failed to parse ICS file: {e}")
            return IcsParsingError(f"Failed to parse ICS file: {e}")

        events = []
        for event in calendar.events:
            if _is_recurring_event(event):
                return RecurringEventError(
                    f"Recurring event detected: {event.name=}, {event.extra=}. We do not support recurring events yet."
                )

            try:
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
            except Exception as e:
                logger.error(f"Failed to parse event: {e}")
                return IcsParsingError(f"Failed to parse event: {e}")
        return events
