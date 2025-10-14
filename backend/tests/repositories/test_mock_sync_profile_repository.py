from datetime import UTC, datetime

import pytest
from pydantic import HttpUrl

from backend.models.rules import Ruleset
from backend.models.sync_profile import (
    ScheduleSource,
    SyncProfile,
    SyncProfileStatus,
    SyncProfileStatusType,
    SyncTrigger,
    SyncType,
    TargetCalendar,
)
from backend.repositories.sync_profile_repository import MockSyncProfileRepository
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
        schedule_source=ScheduleSource(url=HttpUrl("https://example.com/calendar.ics")),
        target_calendar=TargetCalendar(
            id="cal1",
            title="My Calendar",
            description="My Calendar",
            provider_account_id="acc1",
            provider_account_email="test@example.com",
        ),
        status=SyncProfileStatus(
            type=SyncProfileStatusType.NOT_STARTED,
            sync_trigger=SyncTrigger.MANUAL,
            sync_type=SyncType.REGULAR,
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
    repo.save_sync_profile(sample_sync_profile)

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
    repo.save_sync_profile(sample_sync_profile)
    repo.save_sync_profile(profile2)
    repo.save_sync_profile(other_user_profile)

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
    repo.save_sync_profile(sample_sync_profile)
    repo.save_sync_profile(profile2)

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
    repo.save_sync_profile(active_profile)
    repo.save_sync_profile(in_progress_profile)
    repo.save_sync_profile(deleting_profile)

    # List active profiles
    active_profiles = repo.list_all_active_sync_profiles()
    assert len(active_profiles) == 1
    assert active_profiles[0].id == "profile1"


def test_delete_sync_profile(
    repo: MockSyncProfileRepository, sample_sync_profile: SyncProfile
) -> None:
    # Store and then delete profile
    repo.save_sync_profile(sample_sync_profile)
    repo.delete_sync_profile(sample_sync_profile.user_id, sample_sync_profile.id)

    # Verify deletion
    assert (
        repo.get_sync_profile(sample_sync_profile.user_id, sample_sync_profile.id)
        is None
    )


def test_save_sync_profile_updates_existing_profile(
    repo: MockSyncProfileRepository, sample_sync_profile: SyncProfile
) -> None:
    # Store the profile
    repo.save_sync_profile(sample_sync_profile)

    # Update the profile
    sample_sync_profile.title = "Updated Title"
    repo.save_sync_profile(sample_sync_profile)

    # Retrieve the profile
    retrieved = repo.get_sync_profile(
        sample_sync_profile.user_id, sample_sync_profile.id
    )

    assert retrieved is not None
    assert retrieved == sample_sync_profile
