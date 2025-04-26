from unittest.mock import Mock

import pytest

from functions.bootstrap import bootstrap_event_bus
from functions.repositories.sync_stats_repository import MockSyncStatsRepository
from functions.shared.domain_events import (
    IcsFetched,
    SyncFailed,
    SyncProfileCreated,
    SyncSucceeded,
    UserCreated,
)


@pytest.fixture
def ics_file_storage() -> Mock:
    return Mock()


@pytest.fixture
def dev_notification_service() -> Mock:
    return Mock()


@pytest.fixture
def sync_stats_repo() -> MockSyncStatsRepository:
    return MockSyncStatsRepository()


@pytest.fixture
def event_bus(
    ics_file_storage: Mock,
    dev_notification_service: Mock,
    sync_stats_repo: Mock,
):
    return bootstrap_event_bus(
        ics_file_storage=ics_file_storage,
        dev_notification_service=dev_notification_service,
        sync_stats_repo=sync_stats_repo,
    )


def test_handle_ics_fetched(event_bus, ics_file_storage) -> None:
    # Given
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


def test_handle_sync_succeeded(event_bus, sync_stats_repo) -> None:
    user_id = "user123"

    # Given
    assert sync_stats_repo.get_daily_sync_count(user_id) == 0
    event = SyncSucceeded(
        user_id=user_id,
        sync_profile_id="profile123",
    )

    # When
    event_bus.publish(event)

    # Then
    assert sync_stats_repo.get_daily_sync_count(event.user_id) == 1


def test_handle_sync_failed_no_increment(event_bus, sync_stats_repo) -> None:
    user_id = "user123"

    # Given
    assert sync_stats_repo.get_daily_sync_count(user_id) == 0
    event = SyncFailed(
        user_id=user_id,
        sync_profile_id="profile123",
        error_type="IcsSourceError",
        error_message="Failed to fetch calendar",
        formatted_traceback="Traceback (most recent call last):\n...",
    )

    # When
    event_bus.publish(event)

    # Then
    assert sync_stats_repo.get_daily_sync_count(user_id) == 0
