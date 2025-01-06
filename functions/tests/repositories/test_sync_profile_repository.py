# tests/test_sync_profile_repository.py

from datetime import datetime
from pydantic import HttpUrl
import pytest
from mockfirestore import MockFirestore

from functions.models.sync_profile import (
    SyncProfile,
    SyncProfileStatus,
    SyncProfileStatusType,
    ScheduleSource,
    TargetCalendar,
)
from functions.repositories.sync_profile_repository import (
    FirestoreSyncProfileRepository,
)


@pytest.fixture
def mock_db():
    """Provides a fresh MockFirestore instance per test, then resets it."""
    db = MockFirestore()
    yield db
    db.reset()


sync_profile1 = SyncProfile(
    id="syncProf_ABC",
    user_id="user123",
    title="My Sync Profile 1",
    scheduleSource=ScheduleSource(url=HttpUrl("https://example.com/cal1.ics")),
    targetCalendar=TargetCalendar(
        id="calendar123",
        title="MyCalendar",
        description="",
        providerAccountId="google_user_789",
        providerAccountEmail="test@example.com",
    ),
    status=SyncProfileStatus(
        type=SyncProfileStatusType.IN_PROGRESS,
        updatedAt=datetime(2024, 12, 24),
    ),
    created_at=datetime(2024, 12, 23),
    lastSuccessfulSync=None,
)
sync_profile2 = SyncProfile(
    id="syncProf_XYZ",
    user_id="user123",
    title="My Sync Profile 2",
    scheduleSource=ScheduleSource(url=HttpUrl("https://example.com/cal1.ics")),
    targetCalendar=TargetCalendar(
        id="calendar123",
        title="MyCalendar",
        description="",
        providerAccountId="google_user_789",
        providerAccountEmail="test@example.com",
    ),
    status=SyncProfileStatus(
        type=SyncProfileStatusType.IN_PROGRESS,
        updatedAt=datetime(2024, 12, 24),
    ),
    created_at=datetime(2024, 12, 23),
    lastSuccessfulSync=None,
)


def test_get_sync_profile_not_found(mock_db):
    repo = FirestoreSyncProfileRepository(db=mock_db)
    user_id = "user123"
    sync_profile_id = "syncProf_ABC"

    result = repo.get_sync_profile(user_id, sync_profile_id)
    assert result is None


def test_get_sync_profile_found(mock_db):
    repo = FirestoreSyncProfileRepository(db=mock_db)
    sync_profile_id = "syncProf_ABC"
    user_id = "user123"

    sync_profile = SyncProfile(
        id=sync_profile_id,
        user_id=user_id,
        title="My Sync Profile",
        scheduleSource=ScheduleSource(url=HttpUrl("https://example.com/cal.ics")),
        targetCalendar=TargetCalendar(
            id="calendar123",
            title="MyCalendar",
            description="",
            providerAccountId="google_user_789",
            providerAccountEmail="test@example.com",
        ),
        status=SyncProfileStatus(
            type=SyncProfileStatusType.SUCCESS,
            message=None,
            syncTrigger=None,
            syncType=None,
            updatedAt=datetime(2024, 12, 24),
        ),
        ruleset=None,
        ruleset_error=None,
        created_at=datetime(2024, 12, 23),
        lastSuccessfulSync=None,
    )

    # Create the document in mock DB
    mock_db.collection("users").document(user_id).collection("syncProfiles").document(
        sync_profile_id
    ).set(sync_profile.model_dump())

    result = repo.get_sync_profile(user_id, sync_profile_id)
    assert result is not None
    assert result.title == "My Sync Profile"
    assert result.status.type == SyncProfileStatusType.SUCCESS


def test_list_user_sync_profiles(mock_db):
    repo = FirestoreSyncProfileRepository(db=mock_db)
    user_id = "user123"

    # Create two profiles in the same user's subcollection
    mock_db.collection("users").document(user_id).collection("syncProfiles").document(
        "p1"
    ).set(sync_profile1.model_dump())
    mock_db.collection("users").document(user_id).collection("syncProfiles").document(
        "p2"
    ).set(sync_profile2.model_dump())

    profiles = repo.list_user_sync_profiles(user_id)
    assert len(profiles) == 2
    assert sync_profile1 in profiles and sync_profile2 in profiles


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


def test_update_sync_profile_status(mock_db):
    repo = FirestoreSyncProfileRepository(db=mock_db)
    user_id = "user123"
    sync_profile_id = "syncProf_ABC"

    # Create an initial profile doc
    mock_db.collection("users").document(user_id).collection("syncProfiles").document(
        sync_profile_id
    ).set(sync_profile1.model_dump())

    new_status = SyncProfileStatus(
        type=SyncProfileStatusType.FAILED, message="An error occurred"
    )

    repo.update_sync_profile_status(user_id, sync_profile_id, new_status)

    updated = repo.get_sync_profile(user_id=user_id, sync_profile_id=sync_profile_id)
    assert updated is not None

    assert updated.status == new_status
