from datetime import datetime, timezone
from firebase_functions import logger
from typing import List, Optional
from .middleware.middleware import Middleware
from .google_calendar_manager import GoogleCalendarManager
from .ics_parser import IcsParser
from .ics_source import UrlIcsSource
from google.cloud import storage


def perform_synchronization(
    sync_profile_id: str,  # This value is inserted as a property in events to avoid deleting user events
    ics_source_url: str,
    target_calendar_id: str,
    service,
    sync_trigger: str,
    firebase_storage_bucket: storage.Bucket,
    middlewares: Optional[List[Middleware]] = None,
) -> None:
    try:
        ics_str = UrlIcsSource(
            ics_source_url
        ).get_ics_string()  # TODO : Add proper error when url is invalid
    except Exception as e:
        logger.error(f"Failed to get ics string: {e}")
        raise e

    try:
        events = list(set(IcsParser().parse(ics_str)))
    except Exception as e:
        logger.error(f"Failed to parse ics: {e}")
        raise e

    logger.info(f"Found {len(events)} events in ics")

    # Store ics string in firebase storage
    try:
        filename = f"{sync_profile_id}_{datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')}.ics"
        blob = firebase_storage_bucket.blob(filename)

        blob.metadata = {
            "sourceUrl": ics_source_url,
            "syncProfileId": sync_profile_id,
            "syncTrigger": sync_trigger,
            "blob_created_at": datetime.now(timezone.utc).isoformat(),
        }
        blob.upload_from_string(ics_str, content_type="text/calendar")
        logger.info(f"Stored ics string in firebase storage: {filename}")

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

    if not events:
        logger.warn("No events to synchronize")
        return

    logger.info(f"{len(events)} events after applying middlewares")

    calendar_manager = GoogleCalendarManager(service, target_calendar_id)

    calendar_manager.test_authorization()

    separation_dt = datetime.now(timezone.utc)

    if sync_trigger == "on_create":
        return calendar_manager.create_events(events, sync_profile_id)

    # TODO : Only update events that have changed
    future_events_ids = calendar_manager.get_events_ids_from_sync_profile(
        sync_profile_id, separation_dt
    )
    logger.info(f"Found {len(future_events_ids)} future events to delete")

    calendar_manager.delete_events(future_events_ids)

    new_events = [event for event in events if event.end > separation_dt]

    logger.info(f"Found {len(new_events)} new events to insert")

    calendar_manager.create_events(new_events, sync_profile_id)
