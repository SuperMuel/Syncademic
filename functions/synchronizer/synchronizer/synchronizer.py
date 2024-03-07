from dataclasses import dataclass, replace
from typing import Optional
from synchronizer.synchronizer.google_calendar_manager import GoogleCalendarManager
from synchronizer.synchronizer.ics_parser import IcsParser
from synchronizer.synchronizer.ics_source import UrlIcsSource
from synchronizer.synchronizer.event import Event


@dataclass(frozen=True)
class SynchronizationResult:
    success: bool
    error: Optional[str] = None


def _mark_events_with_syncademic(event: Event, syncConfigId: str) -> Event:
    """Mark events with syncademic to prevent deleting user events.

    Uses extended_properties to store the syncConfig id.
    """
    extended_properties = event.extended_properties or {}

    if "private" not in extended_properties:
        extended_properties["private"] = {}

    extended_properties["private"].update({"syncademic": syncConfigId})

    return replace(event, extended_properties=extended_properties)


def perform_synchronization(
    syncConfigId: str,  # hidden in events to avoid deleting user events
    icsSourceUrl: str,
    targetCalendarId: str,
    service,
) -> SynchronizationResult:
    # TODO : delete previous events

    ics_str = UrlIcsSource(icsSourceUrl).get_ics_string()

    events = IcsParser().parse(ics_str)

    #! VERY IMPORTANT : MARK EVENTS WITH SYNCADAMIA TO PREVENT DELETING USER EVENTS
    events = [_mark_events_with_syncademic(event, syncConfigId) for event in events]

    # TODO : add middleware for events

    GoogleCalendarManager(service, targetCalendarId).create_events(events)

    # TODO : improve synchronization result
    return SynchronizationResult(success=True)
