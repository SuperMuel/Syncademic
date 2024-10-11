from datetime import datetime, timezone
from firebase_functions import logger
from typing import List, Literal, Optional

from functions.src.rules.models import Ruleset
from functions.src.synchronizer.ics_cache import IcsFileStorage
from .middleware.middleware import Middleware
from .google_calendar_manager import GoogleCalendarManager
from .ics_parser import IcsParser
from .ics_source import UrlIcsSource

SyncTrigger = Literal["on_create", "manual", "scheduled"]


def perform_synchronization(
    sync_profile_id: str,  # This value is inserted as a property in events to avoid deleting user events
    sync_trigger: SyncTrigger,
    ics_source: UrlIcsSource,
    ics_parser: IcsParser,
    ics_cache: IcsFileStorage,
    calendar_manager: GoogleCalendarManager,
    middlewares: Optional[List[Middleware]] = None,
    rule_set: Ruleset | None = None,
) -> None:
    # Temporary : only one of middlewares or ruleset can be provided, not both
    assert not (
        middlewares and rule_set
    ), "Only one of middlewares or ruleset can be provided"

    try:
        ics_str = ics_source.get_ics_string()
    except Exception as e:
        logger.error(f"Failed to get ics string: {e}")
        raise e

    try:
        events = list(set(ics_parser.parse(ics_str)))
    except Exception as e:
        logger.error(f"Failed to parse ics: {e}")
        raise e

    logger.info(f"Found {len(events)} events in ics")

    # Store the ics string for later use
    try:
        ics_cache.save_to_cache(
            sync_profile_id=sync_profile_id,
            sync_trigger=sync_trigger,
            ics_source=ics_source,
            ics_str=ics_str,
        )
    except Exception as e:
        logger.error(f"Failed to store ics string in firebase storage. {e}")
        # Do not raise, we want to continue the execution

    try:
        if middlewares:
            logger.info(f"Applying {len(middlewares)} middlewares")
            for middleware in middlewares:
                events = middleware(events)
    except Exception as e:
        logger.error(f"Failed to apply middlewares: {e}")
        raise e

    try:
        if rule_set:
            logger.info(f"Applying {len(rule_set.rules)} rules")
            events = rule_set.apply(events)
    except Exception as e:
        logger.error(f"Failed to apply rules: {e}")
        raise e

    if not events:
        logger.warn("No events to synchronize")
        return

    logger.info(f"{len(events)} events after applying middlewares")

    if sync_trigger == "on_create":
        return calendar_manager.create_events(events, sync_profile_id)

    separation_dt = datetime.now(timezone.utc)

    # TODO : Only update events that have changed
    future_events_ids = calendar_manager.get_events_ids_from_sync_profile(
        sync_profile_id, separation_dt
    )
    logger.info(f"Found {len(future_events_ids)} future events to delete")

    calendar_manager.delete_events(future_events_ids)

    new_events = [event for event in events if event.end > separation_dt]

    logger.info(f"Found {len(new_events)} new events to insert")

    calendar_manager.create_events(new_events, sync_profile_id)
