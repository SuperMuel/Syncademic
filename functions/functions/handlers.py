from functions.services.dev_notification_service import IDevNotificationService
from functions.shared.domain_events import (
    IcsFetched,
    SyncFailed,
    SyncProfileCreated,
    UserCreated,
)
from functions.synchronizer.ics_cache import IcsFileStorage


def handle_ics_fetched(event: IcsFetched, ics_file_storage: IcsFileStorage) -> None:
    """
    Stores the ICS data and metadata from an IcsFetched event in the ICS file cache.
    
    Args:
        event: The IcsFetched event containing the ICS string and associated metadata.
    """
    ics_file_storage.save_to_cache(
        ics_str=event.ics_str,
        metadata=event.metadata,
    )


def handle_sync_profile_created(
    event: SyncProfileCreated,
    dev_notification_service: IDevNotificationService,
) -> None:
    """
    Handles a SyncProfileCreated event by notifying the developer notification service.
    
    Invokes the notification service to process actions related to the creation of a new sync profile.
    """
    dev_notification_service.on_new_sync_profile(event)


def handle_user_created(
    event: UserCreated,
    dev_notification_service: IDevNotificationService,
) -> None:
    """
    Handles a UserCreated event by notifying the developer notification service.
    
    Invokes the notification service to process a newly created user event.
    """
    dev_notification_service.on_new_user(event)


def handle_sync_failed(
    event: SyncFailed,
    dev_notification_service: IDevNotificationService,
) -> None:
    """
    Handles a synchronization failure event by notifying the developer notification service.
    
    Args:
        event: The SyncFailed event containing details of the synchronization failure.
    """
    dev_notification_service.on_sync_failed(event)
