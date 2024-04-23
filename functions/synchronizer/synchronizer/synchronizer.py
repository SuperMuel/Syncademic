from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from typing import List, Optional
from .middleware.middleware import Middleware
from .google_calendar_manager import GoogleCalendarManager
from .ics_parser import IcsParser
from .ics_source import UrlIcsSource


logger = logging.getLogger(__name__)  # TODO: get logger from cloud functions


def perform_synchronization(
    # TODO : change parameters to snake_case
    syncProfileId: str,  # This value is inserted as a property in events to avoid deleting user events
    icsSourceUrl: str,
    targetCalendarId: str,
    service,
    syncTrigger: str,
    middlewares: Optional[List[Middleware]] = None,
) -> None:
    try:
        ics_str = UrlIcsSource(
            icsSourceUrl
        ).get_ics_string()  # TODO : Add proper error when url is invalid
    except Exception as e:
        logger.error(f"Failed to get ics string: {e}")
        raise e

    try:
        events = list(set(IcsParser().parse(ics_str)))
    except Exception as e:
        logger.error(f"Failed to parse ics: {e}")
        raise e

    try:
        if middlewares:
            for middleware in middlewares:
                events = middleware(events)
    except Exception as e:
        logger.error(f"Failed to apply middlewares: {e}")
        raise e

    if not events:
        logger.warning("No events to synchronize")
        return

    calendar_manager = GoogleCalendarManager(service, targetCalendarId)

    calendar_manager.test_authorization()

    separation_dt = datetime.now(timezone.utc)

    if syncTrigger == "on_create":
        return calendar_manager.create_events(events, syncProfileId)

    # TODO : Only update events that have changed
    future_events_ids = calendar_manager.get_events_ids_from_sync_profile(
        syncProfileId, separation_dt
    )

    calendar_manager.delete_events(future_events_ids)

    new_events = [event for event in events if event.end > separation_dt]

    calendar_manager.create_events(new_events, syncProfileId)
