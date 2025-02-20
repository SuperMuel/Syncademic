from datetime import UTC, datetime

import pytest
from pydantic import HttpUrl

from functions.models.rules import Ruleset
from functions.models.sync_profile import (
    ScheduleSource,
    SyncProfile,
    SyncProfileStatus,
    SyncProfileStatusType,
    SyncTrigger,
    SyncType,
    TargetCalendar,
)
from functions.repositories.sync_profile_repository import MockSyncProfileRepository
from tests.util import VALID_RULESET


@pytest.fixture
def repo() -> MockSyncProfileRepository:
    return MockSyncProfileRepository()


@pytest.fixture
def sample_sync_profile() -> SyncProfile:
    return SyncProfile(
        id="profile1",
        user_id="user1",
        title="Test Profile",
        scheduleSource=ScheduleSource(url=HttpUrl("https://example.com/calendar.ics")),
        targetCalendar=TargetCalendar(
            id="cal1",
            title="My Calendar",
            description="My Calendar",
            providerAccountId="acc1",
            providerAccountEmail="test@example.com",
        ),
        status=SyncProfileStatus(
            type=SyncProfileStatusType.NOT_STARTED,
            syncTrigger=SyncTrigger.MANUAL,
            syncType=SyncType.REGULAR,
        ),
        created_at=datetime.now(UTC),
    )


def test_get_nonexistent_profile(repo: MockSyncProfileRepository) -> None:
    profile = repo.get_sync_profile("nonexistent", "nonexistent")
    assert profile is None


def test_store_and_get_profile(
    repo: MockSyncProfileRepository, sample_sync_profile: SyncProfile
) -> None:
    # Store the profile
    repo.store_sync_profile(sample_sync_profile)

    # Retrieve it
    retrieved = repo.get_sync_profile(
        sample_sync_profile.user_id, sample_sync_profile.id
    )
    assert retrieved == sample_sync_profile


def test_list_user_sync_profiles(
    repo: MockSyncProfileRepository, sample_sync_profile: SyncProfile
) -> None:
    # Create a second profile for the same user
    profile2 = sample_sync_profile.model_copy(update={"id": "profile2"})

    # Create a profile for a different user
    other_user_profile = sample_sync_profile.model_copy(
        update={"id": "profile3", "user_id": "user2"}
    )

    # Store all profiles
    repo.store_sync_profile(sample_sync_profile)
    repo.store_sync_profile(profile2)
    repo.store_sync_profile(other_user_profile)

    # List profiles for user1
    user_profiles = repo.list_user_sync_profiles("user1")
    assert len(user_profiles) == 2
    assert all(p.user_id == "user1" for p in user_profiles)

    # List profiles for user2
    user2_profiles = repo.list_user_sync_profiles("user2")
    assert len(user2_profiles) == 1
    assert user2_profiles[0].id == "profile3"


def test_list_all_sync_profiles(
    repo: MockSyncProfileRepository, sample_sync_profile: SyncProfile
) -> None:
    # Store two profiles
    profile2 = sample_sync_profile.model_copy(
        update={"id": "profile2", "user_id": "user2"}
    )
    repo.store_sync_profile(sample_sync_profile)
    repo.store_sync_profile(profile2)

    # List all profiles
    all_profiles = repo.list_all_sync_profiles()
    assert len(all_profiles) == 2


def test_list_all_active_sync_profiles(
    repo: MockSyncProfileRepository, sample_sync_profile: SyncProfile
) -> None:
    # Create profiles with different statuses
    active_profile = sample_sync_profile
    in_progress_profile = sample_sync_profile.model_copy(
        update={
            "id": "profile2",
            "status": SyncProfileStatus(type=SyncProfileStatusType.IN_PROGRESS),
        }
    )
    deleting_profile = sample_sync_profile.model_copy(
        update={
            "id": "profile3",
            "status": SyncProfileStatus(type=SyncProfileStatusType.DELETING),
        }
    )

    # Store all profiles
    repo.store_sync_profile(active_profile)
    repo.store_sync_profile(in_progress_profile)
    repo.store_sync_profile(deleting_profile)

    # List active profiles
    active_profiles = repo.list_all_active_sync_profiles()
    assert len(active_profiles) == 1
    assert active_profiles[0].id == "profile1"


def test_update_sync_profile_status(
    repo: MockSyncProfileRepository, sample_sync_profile: SyncProfile
) -> None:
    # Store initial profile
    repo.store_sync_profile(sample_sync_profile)

    # Update status
    new_status = SyncProfileStatus(
        type=SyncProfileStatusType.SUCCESS,
        message="Sync completed",
        syncTrigger=SyncTrigger.MANUAL,
        syncType=SyncType.FULL,
    )
    repo.update_sync_profile_status(
        user_id=sample_sync_profile.user_id,
        sync_profile_id=sample_sync_profile.id,
        status=new_status,
    )

    # Verify update
    updated = repo.get_sync_profile(sample_sync_profile.user_id, sample_sync_profile.id)
    assert updated is not None
    assert updated.status == new_status


def test_delete_sync_profile(
    repo: MockSyncProfileRepository, sample_sync_profile: SyncProfile
) -> None:
    # Store and then delete profile
    repo.store_sync_profile(sample_sync_profile)
    repo.delete_sync_profile(sample_sync_profile.user_id, sample_sync_profile.id)

    # Verify deletion
    assert (
        repo.get_sync_profile(sample_sync_profile.user_id, sample_sync_profile.id)
        is None
    )


def test_update_timestamps(
    repo: MockSyncProfileRepository, sample_sync_profile: SyncProfile
) -> None:
    # Store initial profile
    repo.store_sync_profile(sample_sync_profile)
    initial_created_at = sample_sync_profile.created_at

    # Test default behavior (current timestamp)
    repo.update_created_at(sample_sync_profile.user_id, sample_sync_profile.id)
    repo.update_last_successful_sync(
        sample_sync_profile.user_id, sample_sync_profile.id
    )

    # Verify updates with default behavior
    updated = repo.get_sync_profile(sample_sync_profile.user_id, sample_sync_profile.id)
    assert updated is not None
    assert updated.created_at > initial_created_at
    assert updated.lastSuccessfulSync is not None

    # Test with custom datetime
    custom_dt = datetime(2024, 1, 1, tzinfo=UTC)
    repo.update_created_at(
        sample_sync_profile.user_id, sample_sync_profile.id, created_at=custom_dt
    )

    # Verify update with custom datetime
    updated = repo.get_sync_profile(sample_sync_profile.user_id, sample_sync_profile.id)
    assert updated is not None
    assert updated.created_at == custom_dt


def test_update_ruleset(
    repo: MockSyncProfileRepository, sample_sync_profile: SyncProfile
) -> None:
    # Store initial profile
    repo.store_sync_profile(sample_sync_profile)

    # Update ruleset
    repo.update_ruleset(
        sample_sync_profile.user_id, sample_sync_profile.id, VALID_RULESET
    )

    # Verify update
    updated = repo.get_sync_profile(sample_sync_profile.user_id, sample_sync_profile.id)
    assert updated is not None
    assert updated.ruleset == VALID_RULESET
    assert updated.ruleset_error is None


def test_update_ruleset_error(
    repo: MockSyncProfileRepository, sample_sync_profile: SyncProfile
) -> None:
    # Store initial profile
    repo.store_sync_profile(sample_sync_profile)

    # Update ruleset error
    error_message = "Failed to generate ruleset"
    repo.update_ruleset_error(
        sample_sync_profile.user_id, sample_sync_profile.id, error_message
    )

    # Verify update
    updated = repo.get_sync_profile(sample_sync_profile.user_id, sample_sync_profile.id)
    assert updated is not None
    assert updated.ruleset_error == error_message


def test_operations_on_nonexistent_profile(
    repo: MockSyncProfileRepository, sample_sync_profile: SyncProfile
) -> None:
    """Test that operations on non-existent profiles don't raise exceptions"""
    # All these should complete without raising exceptions
    repo.update_sync_profile_status(
        user_id="nonexistent",
        sync_profile_id="nonexistent",
        status=SyncProfileStatus(type=SyncProfileStatusType.SUCCESS),
    )
    repo.update_created_at("nonexistent", "nonexistent")
    repo.update_last_successful_sync("nonexistent", "nonexistent")
    repo.update_ruleset_error("nonexistent", "nonexistent", "error")
    repo.update_ruleset("nonexistent", "nonexistent", VALID_RULESET)
    repo.delete_sync_profile("nonexistent", "nonexistent")
