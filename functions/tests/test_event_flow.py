from unittest.mock import Mock

import pytest

from functions.bootstrap import bootstrap_event_bus
from functions.shared.domain_events import (
    IcsFetched,
    SyncFailed,
    SyncProfileCreated,
    UserCreated,
)


@pytest.fixture
def ics_file_storage() -> Mock:
    """
    Provides a mock ICS file storage service for use in tests.
    
    Returns:
        Mock: A mock object simulating the ICS file storage service.
    """
    return Mock()


@pytest.fixture
def dev_notification_service() -> Mock:
    """
    Provides a mocked developer notification service for use in tests.
    
    Returns:
        Mock: A mock instance simulating the developer notification service.
    """
    return Mock()


@pytest.fixture
def event_bus(ics_file_storage: Mock, dev_notification_service: Mock):
    """
    Initializes and returns an event bus configured with mocked ICS file storage and developer notification services.
    
    Returns:
        An event bus instance set up for testing with the provided mock services.
    """
    return bootstrap_event_bus(
        ics_file_storage=ics_file_storage,
        dev_notification_service=dev_notification_service,
    )


def test_handle_ics_fetched(event_bus, ics_file_storage) -> None:
    # Given
    """
    Tests that publishing an IcsFetched event triggers saving the ICS data to cache.
    
    Verifies that the event bus routes the IcsFetched event to the ICS file storage's
    save_to_cache method with the correct ICS string and metadata.
    """
    event = IcsFetched(
        ics_str="BEGIN:VCALENDAR\nEND:VCALENDAR",
        metadata={"url": "test.ics"},
    )

    # When
    event_bus.publish(event)

    # Then
    ics_file_storage.save_to_cache.assert_called_once_with(
        ics_str=event.ics_str,
        metadata=event.metadata,
    )


def test_handle_sync_profile_created(event_bus, dev_notification_service) -> None:
    # Given
    """
    Tests that publishing a SyncProfileCreated event triggers the developer notification service.
    
    Verifies that when a SyncProfileCreated event is published to the event bus, the developer notification service's on_new_sync_profile method is called once with the event.
    """
    event = SyncProfileCreated(
        user_id="user123",
        sync_profile_id="profile123",
    )

    # When
    event_bus.publish(event)

    # Then
    dev_notification_service.on_new_sync_profile.assert_called_once_with(event)


def test_handle_user_created(event_bus, dev_notification_service) -> None:
    # Given
    """
    Tests that publishing a UserCreated event triggers the developer notification service.
    
    Verifies that when a UserCreated event is published to the event bus, the developer notification service's on_new_user method is called once with the event.
    """
    event = UserCreated(
        user_id="user123",
        email="test@example.com",
        display_name="Test User",
        provider_id="google.com",
    )

    # When
    event_bus.publish(event)

    # Then
    dev_notification_service.on_new_user.assert_called_once_with(event)


def test_handle_sync_failed(event_bus, dev_notification_service) -> None:
    # Given
    event = SyncFailed(
        user_id="user123",
        sync_profile_id="profile123",
        error_type="IcsSourceError",
        error_message="Failed to fetch calendar",
        formatted_traceback="Traceback (most recent call last):\n...",
    )

    # When
    event_bus.publish(event)

    # Then
    dev_notification_service.on_sync_failed.assert_called_once_with(event)
