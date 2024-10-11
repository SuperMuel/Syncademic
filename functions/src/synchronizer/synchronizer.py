from datetime import datetime, timezone
from firebase_functions import logger
from typing import List, Literal, Optional

from src.rules.models import Ruleset
from src.synchronizer.ics_cache import IcsFileStorage
from .middleware.middleware import Middleware
from .google_calendar_manager import GoogleCalendarManager
from .ics_parser import IcsParser
from .ics_source import UrlIcsSource

SyncTrigger = Literal["on_create", "manual", "scheduled"]
SyncType = Literal["full", "regular"]


def perform_synchronization(
    sync_profile_id: str,  # This value is inserted as a property in events to avoid deleting user events
    sync_trigger: SyncTrigger,
    ics_source: UrlIcsSource,
    ics_parser: IcsParser,
    ics_cache: IcsFileStorage,
    calendar_manager: GoogleCalendarManager,
    middlewares: Optional[List[Middleware]] = None,
    rule_set: Ruleset | None = None,
    separation_dt: datetime | None = None,
    sync_type: SyncType = "regular",
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
        events = ics_parser.parse(ics_str)
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
            logger.info(f"{len(events)} events after applying middlewares")
    except Exception as e:
        logger.error(f"Failed to apply middlewares: {e}")
        raise e

    try:
        if rule_set:
            logger.info(f"Applying {len(rule_set.rules)} rules")
            events = rule_set.apply(events)
            logger.info(f"{len(events)} events after applying rules")
    except Exception as e:
        logger.error(f"Failed to apply rules: {e}")
        raise e

    if not events:
        logger.warn("No events to synchronize")

    if sync_trigger == "on_create":
        return calendar_manager.create_events(events, sync_profile_id)

    if sync_type == "regular":
        logger.info("Performing regular synchronization, only updating future events")

        separation_dt = separation_dt or datetime.now(timezone.utc)
        events_to_delete = calendar_manager.get_events_ids_from_sync_profile(
            sync_profile_id, separation_dt
        )
        new_events = [event for event in events if event.end > separation_dt]

    elif sync_type == "full":
        logger.info("Performing full synchronization, deleting all events")

        events_to_delete = calendar_manager.get_events_ids_from_sync_profile(
            sync_profile_id, min_dt=None
        )
        new_events = events
    else:
        raise ValueError(f"Invalid sync_type: {sync_type}")

    if events_to_delete:
        logger.info(f"Found {len(events_to_delete)} events to delete")
        calendar_manager.delete_events(events_to_delete)
    else:
        logger.info("No events to delete")

    if new_events:
        logger.info(f"Found {len(new_events)} new events to insert")
        calendar_manager.create_events(new_events, sync_profile_id)
    else:
        logger.info("No new events to insert")