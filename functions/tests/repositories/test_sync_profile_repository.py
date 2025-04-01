from datetime import datetime, timezone
from pydantic import HttpUrl
import pytest
from mockfirestore import MockFirestore

from functions.models.rules import Ruleset
from functions.models.sync_profile import (
    SyncProfile,
    SyncProfileStatus,
    SyncProfileStatusType,
    ScheduleSource,
    TargetCalendar,
    SyncTrigger,
    SyncType,
)
from functions.repositories.sync_profile_repository import (
    FirestoreSyncProfileRepository,
)
from tests.util import VALID_RULESET


@pytest.fixture
def mock_db():
    """Provides a fresh MockFirestore instance per test, then resets it."""
    db = MockFirestore()
    yield db
    db.reset()


@pytest.fixture
def sample_sync_profile() -> SyncProfile:
    """Provides a reusable sample sync profile for testing."""
    return SyncProfile(
        id="test_profile_id",
        user_id="test_user_id",
        title="Test Sync Profile",
        scheduleSource=ScheduleSource(url=HttpUrl("https://example.com/calendar.ics")),
        targetCalendar=TargetCalendar(
            id="calendar123",
            title="Test Calendar",
            description="Test calendar description",
            providerAccountId="google_user_456",
            providerAccountEmail="test@example.com",
        ),
        status=SyncProfileStatus(
            type=SyncProfileStatusType.NOT_STARTED,
            syncTrigger=SyncTrigger.MANUAL,
            syncType=SyncType.REGULAR,
            updatedAt=datetime(2024, 12, 24, tzinfo=timezone.utc),
        ),
        created_at=datetime(2024, 12, 23, tzinfo=timezone.utc),
        lastSuccessfulSync=None,
        ruleset=VALID_RULESET,
    )


def test_save_sync_profile_create_new(mock_db, sample_sync_profile: SyncProfile):
    """Test creating a new sync profile."""
    repo = FirestoreSyncProfileRepository(db=mock_db)
    user_id = sample_sync_profile.user_id
    sync_profile_id = sample_sync_profile.id

    # Save the profile
    repo.save_sync_profile(sample_sync_profile)

    # Verify it was stored in the DB
    doc = (
        mock_db.collection("users")
        .document(user_id)
        .collection("syncProfiles")
        .document(sync_profile_id)
        .get()
    )
    assert doc.exists

    # Retrieve it using the repository
    retrieved_profile = repo.get_sync_profile(user_id, sync_profile_id)
    assert retrieved_profile is not None
    assert retrieved_profile == sample_sync_profile


def test_save_sync_profile_update_existing(mock_db, sample_sync_profile: SyncProfile):
    """Test updating an existing sync profile."""
    repo = FirestoreSyncProfileRepository(db=mock_db)
    user_id = sample_sync_profile.user_id
    sync_profile_id = sample_sync_profile.id

    # Save the initial profile
    repo.save_sync_profile(sample_sync_profile)

    # Create a copy of the profile with updated properties
    updated_profile = sample_sync_profile.model_copy(deep=True)
    updated_profile.title = "Updated Profile Title"
    updated_profile.status = SyncProfileStatus(
        type=SyncProfileStatusType.IN_PROGRESS,
        updatedAt=datetime(2024, 12, 25, tzinfo=timezone.utc),
    )
    updated_profile.lastSuccessfulSync = datetime(2024, 12, 25, tzinfo=timezone.utc)

    # Save the updated profile
    repo.save_sync_profile(updated_profile)

    # Retrieve it and verify the updates
    retrieved_profile = repo.get_sync_profile(user_id, sync_profile_id)
    assert retrieved_profile is not None
    assert retrieved_profile == updated_profile


def test_get_sync_profile_not_found(mock_db, sample_sync_profile):
    repo = FirestoreSyncProfileRepository(db=mock_db)
    user_id = sample_sync_profile.user_id
    nonexistent_id = "nonexistent_profile"

    result = repo.get_sync_profile(user_id, nonexistent_id)
    assert result is None


def test_list_user_sync_profiles(mock_db, sample_sync_profile: SyncProfile):
    repo = FirestoreSyncProfileRepository(db=mock_db)
    user_id = sample_sync_profile.user_id

    # Create a second profile with different ID
    second_profile = sample_sync_profile.model_copy(
        update={"id": "second_profile_id"}, deep=True
    )

    # Save both profiles
    repo.save_sync_profile(sample_sync_profile)
    repo.save_sync_profile(second_profile)

    # List profiles for the user
    profiles = repo.list_user_sync_profiles(user_id)

    # Verify we have both profiles
    assert len(profiles) == 2
    profile_ids = [p.id for p in profiles]
    assert sample_sync_profile.id in profile_ids
    assert second_profile.id in profile_ids


# This test is disabled for now because mockfirestore library
# doesn't support collection group queries.
# def test_list_all_sync_profiles(mock_db):
#     repo = FirestoreSyncProfileRepository(db=mock_db)

#     # Create profiles in multiple user docs
#     mock_db.collection("users").document("userA").collection("syncProfiles").document(
#         "p1"
#     ).set(sync_profile1.model_dump())
#     mock_db.collection("users").document("userB").collection("syncProfiles").document(
#         "p2"
#     ).set(sync_profile2.model_dump())

#     all_profiles = repo.list_all_sync_profiles()
#     assert len(all_profiles) == 2
#     assert sync_profile1 in all_profiles and sync_profile2 in all_profiles


def test_delete_sync_profile(mock_db, sample_sync_profile: SyncProfile):
    repo = FirestoreSyncProfileRepository(db=mock_db)
    user_id = sample_sync_profile.user_id
    sync_profile_id = sample_sync_profile.id

    # Save the profile
    repo.save_sync_profile(sample_sync_profile)

    # Verify profile exists before deletion
    profile_before = repo.get_sync_profile(user_id, sync_profile_id)
    assert profile_before is not None

    # Delete the profile
    repo.delete_sync_profile(user_id, sync_profile_id)

    # Verify profile no longer exists
    profile_after = repo.get_sync_profile(user_id, sync_profile_id)
    assert profile_after is None

    # Verify directly in mock DB that document is gone
    doc = (
        mock_db.collection("users")
        .document(user_id)
        .collection("syncProfiles")
        .document(sync_profile_id)
        .get()
    )
    assert not doc.exists


def test_ruleset_stored_as_json_string(mock_db, sample_sync_profile: SyncProfile):
    """Test that the ruleset is stored as a JSON string under the 'ruleset' key in Firestore."""
    repo = FirestoreSyncProfileRepository(db=mock_db)
    user_id = sample_sync_profile.user_id
    sync_profile_id = sample_sync_profile.id

    # Save the profile with the ruleset
    repo.save_sync_profile(sample_sync_profile)

    # Get the raw data from Firestore
    doc_ref = (
        mock_db.collection("users")
        .document(user_id)
        .collection("syncProfiles")
        .document(sync_profile_id)
    )
    doc_data = doc_ref.get().to_dict()

    # Verify the ruleset is stored as a string
    assert (
        "ruleset" in doc_data
    ), "The ruleset key should exist in the Firestore document"
    assert isinstance(
        doc_data["ruleset"], str
    ), "The ruleset should be stored as a string"

    # Validate the ruleset
    ruleset = Ruleset.model_validate_json(doc_data["ruleset"])
    assert ruleset == VALID_RULESET
