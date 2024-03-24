from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from .middleware.middleware import Middleware
from .google_calendar_manager import GoogleCalendarManager
from .ics_parser import IcsParser
from .ics_source import UrlIcsSource


@dataclass(frozen=True)
class SynchronizationResult:
    success: bool
    error: Optional[str] = None


def perform_synchronization(
    syncProfileId: str,  # hidden in events to avoid deleting user events
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

    # TODO : Check if there are events to synchronize. If not, issue a warning and return. Do not delete events.

    calendar_manager = GoogleCalendarManager(service, targetCalendarId)

    calendar_manager.test_authorization()

    separation_dt = datetime.now()

    future_events_ids = calendar_manager.get_events_ids_from_sync_profile(
        syncProfileId, separation_dt
    )

    calendar_manager.delete_events(future_events_ids)

    new_events = [event for event in events if event.end < separation_dt]

    calendar_manager.create_events(new_events, syncProfileId)

    # TODO : improve synchronization result
    return SynchronizationResult(success=True)
