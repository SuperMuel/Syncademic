from dataclasses import dataclass
from typing import List, Optional

from synchronizer.middleware.middleware import Middleware
from .google_calendar_manager import GoogleCalendarManager
from .ics_parser import IcsParser
from .ics_source import UrlIcsSource


@dataclass(frozen=True)
class SynchronizationResult:
    success: bool
    error: Optional[str] = None


def perform_synchronization(
    syncConfigId: str,  # hidden in events to avoid deleting user events
    icsSourceUrl: str,
    targetCalendarId: str,
    service,
    middlewares: Optional[List[Middleware]] = None,
) -> SynchronizationResult:
    # TODO : delete previous events

    ics_str = UrlIcsSource(icsSourceUrl).get_ics_string()

    events = list(set(IcsParser().parse(ics_str)))

    if middlewares:
        for middleware in middlewares:
            events = middleware(events)

    #! VERY IMPORTANT : MARK EVENTS WITH SYNCADAMIA TO PREVENT DELETING USER EVENTS

    # TODO : add middleware for events

    GoogleCalendarManager(service, targetCalendarId).create_events(events, syncConfigId)

    # TODO : improve synchronization result
    return SynchronizationResult(success=True)
