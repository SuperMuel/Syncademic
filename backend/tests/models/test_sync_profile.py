from datetime import datetime, timezone

import pytest
from pydantic import HttpUrl, ValidationError

from backend.models import (
    ScheduleSource,
    SyncProfile,
    SyncProfileStatus,
    SyncProfileStatusType,
    SyncTrigger,
    SyncType,
    TargetCalendar,
)
from backend.models.rules import Ruleset
from tests.util import VALID_RULESET

VALID_SCHEDULE_SOURCE = ScheduleSource(url=HttpUrl("https://example.com/test.ics"))

VALID_TARGET_CALENDAR = TargetCalendar(
    id="test_calendar_id",
    title="My Calendar",
    description="Sample desc",
    providerAccountId="googleUser123",
    providerAccountEmail="user@example.com",
)

VALID_SYNC_PROFILE_STATUS = SyncProfileStatus(
    type=SyncProfileStatusType.IN_PROGRESS,
    syncTrigger=SyncTrigger.SCHEDULED,
    syncType=SyncType.FULL,
)

SYNC_PROFILE_ID = "test_sync_profile_id"
USER_ID = "test_user_id"


def test_sync_profile_valid_minimal():
    profile = SyncProfile(
        id=SYNC_PROFILE_ID,
        user_id=USER_ID,
        title="My New Profile",
        scheduleSource=VALID_SCHEDULE_SOURCE,
        targetCalendar=VALID_TARGET_CALENDAR,
        status=VALID_SYNC_PROFILE_STATUS,
    )

    assert profile.title == "My New Profile"
    assert str(profile.scheduleSource.url) == "https://example.com/test.ics"
    assert profile.status.type == SyncProfileStatusType.IN_PROGRESS
    assert profile.created_at is not None
    assert profile.created_at <= datetime.now(timezone.utc)


def test_sync_profile_empty_id():
    with pytest.raises(ValidationError) as exc_info:
        SyncProfile(
            id="",
            user_id=USER_ID,
            title="My New Profile",
            scheduleSource=VALID_SCHEDULE_SOURCE,
            targetCalendar=VALID_TARGET_CALENDAR,
            status=VALID_SYNC_PROFILE_STATUS,
        )

    assert "string_too_short" in str(exc_info.value)


def test_sync_profile_empty_user_id():
    with pytest.raises(ValidationError) as exc_info:
        SyncProfile(
            id=SYNC_PROFILE_ID,
            user_id="",
            title="My New Profile",
            scheduleSource=VALID_SCHEDULE_SOURCE,
            targetCalendar=VALID_TARGET_CALENDAR,
            status=VALID_SYNC_PROFILE_STATUS,
        )

    assert "string_too_short" in str(exc_info.value)


def test_sync_profile_invalid_url():
    """
    Test that providing an invalid ICS URL raises a ValidationError.
    """
    with pytest.raises(ValidationError) as exc_info:
        ScheduleSource(url="invalidemail")  # type: ignore

    # "value is not a valid URL" comes from pydantic's HttpUrl
    assert "Input should be a valid URL" in str(exc_info.value)


def test_sync_profile_too_short_title():
    """
    Test that providing a title that's too short raises a ValidationError.
    """
    with pytest.raises(ValidationError) as exc_info:
        SyncProfile(
            id=SYNC_PROFILE_ID,
            user_id=USER_ID,
            title="",
            scheduleSource=VALID_SCHEDULE_SOURCE,
            targetCalendar=VALID_TARGET_CALENDAR,
            status=VALID_SYNC_PROFILE_STATUS,
        )

    assert "should have at least 3 characters" in str(exc_info.value)


def test_sync_profile_too_long_title():
    """
    Test that providing a title that's too long raises a ValidationError.
    """
    with pytest.raises(ValidationError) as exc_info:
        SyncProfile(
            id=SYNC_PROFILE_ID,
            user_id=USER_ID,
            title="x" * 51,
            scheduleSource=VALID_SCHEDULE_SOURCE,
            targetCalendar=VALID_TARGET_CALENDAR,
            status=VALID_SYNC_PROFILE_STATUS,
        )

    assert "should have at most 50 characters" in str(exc_info.value)


def test_sync_profile_ruleset_serde_from_and_to_string():
    profile = SyncProfile(
        id=SYNC_PROFILE_ID,
        user_id=USER_ID,
        title="My New Profile",
        scheduleSource=VALID_SCHEDULE_SOURCE,
        targetCalendar=VALID_TARGET_CALENDAR,
        status=VALID_SYNC_PROFILE_STATUS,
        ruleset=VALID_RULESET,
    )

    assert isinstance(profile.ruleset, Ruleset)
    assert profile.ruleset == VALID_RULESET

    profile_dict = profile.model_dump()
    assert isinstance(profile_dict["ruleset"], str)

    deserialised_profile = SyncProfile(**profile_dict)
    assert deserialised_profile.ruleset == VALID_RULESET
    assert deserialised_profile.ruleset == profile.ruleset


def test_sync_profile_update_ruleset_with_new_ruleset():
    """
    Tests updating a SyncProfile's ruleset with a new ruleset instance.
    """
    profile = SyncProfile(
        id=SYNC_PROFILE_ID,
        user_id=USER_ID,
        title="My New Profile",
        scheduleSource=VALID_SCHEDULE_SOURCE,
        targetCalendar=VALID_TARGET_CALENDAR,
        status=VALID_SYNC_PROFILE_STATUS,
        ruleset_error="Previous error",
    )

    # Initially has an error, no ruleset
    assert profile.ruleset is None
    assert profile.ruleset_error == "Previous error"

    # Update with a new ruleset
    profile.update_ruleset(ruleset=VALID_RULESET)

    # Should have ruleset and no error
    assert profile.ruleset == VALID_RULESET
    assert profile.ruleset_error is None


def test_sync_profile_update_ruleset_with_error():
    """
    Tests updating a SyncProfile's ruleset with an error message.
    """
    profile = SyncProfile(
        id=SYNC_PROFILE_ID,
        user_id=USER_ID,
        title="My New Profile",
        scheduleSource=VALID_SCHEDULE_SOURCE,
        targetCalendar=VALID_TARGET_CALENDAR,
        status=VALID_SYNC_PROFILE_STATUS,
        ruleset=VALID_RULESET,
    )

    # Initially has a ruleset, no error
    assert profile.ruleset == VALID_RULESET
    assert profile.ruleset_error is None

    # Update with an error
    profile.update_ruleset(error="Failed to process ruleset")

    # Should have error and no ruleset
    assert profile.ruleset is None
    assert profile.ruleset_error == "Failed to process ruleset"


def test_sync_profile_update_ruleset_validation_error():
    """
    Tests that providing both ruleset and error to update_ruleset raises ValueError.
    """
    profile = SyncProfile(
        id=SYNC_PROFILE_ID,
        user_id=USER_ID,
        title="My New Profile",
        scheduleSource=VALID_SCHEDULE_SOURCE,
        targetCalendar=VALID_TARGET_CALENDAR,
        status=VALID_SYNC_PROFILE_STATUS,
    )

    with pytest.raises(ValueError) as exc_info:
        profile.update_ruleset(ruleset=VALID_RULESET, error="This should fail")

    # Check error message is as expected
    assert "either provide a new ruleset or an error, but not both" in str(
        exc_info.value
    )


def test_sync_profile_validate_ruleset_and_error():
    """
    Tests the model validator that prevents both ruleset and ruleset_error from being set.
    """
    with pytest.raises(ValueError) as exc_info:
        SyncProfile(
            id=SYNC_PROFILE_ID,
            user_id=USER_ID,
            title="My New Profile",
            scheduleSource=VALID_SCHEDULE_SOURCE,
            targetCalendar=VALID_TARGET_CALENDAR,
            status=VALID_SYNC_PROFILE_STATUS,
            ruleset=VALID_RULESET,
            ruleset_error="This should fail",
        )

    # Check error message is as expected
    assert "ruleset and ruleset_error cannot both be set" in str(exc_info.value)


def test_sync_profile_model_validate_default_created_at():
    """
    Tests that SyncProfile.model_validate() sets a default created_at when not provided.
    """
    from datetime import datetime, timezone

    # Create data without created_at
    data = {
        "id": SYNC_PROFILE_ID,
        "user_id": USER_ID,
        "title": "My New Profile",
        "scheduleSource": VALID_SCHEDULE_SOURCE.model_dump(),
        "targetCalendar": VALID_TARGET_CALENDAR.model_dump(),
        "status": VALID_SYNC_PROFILE_STATUS.model_dump(),
    }

    # Get current time for comparison
    before_validation = datetime.now(timezone.utc)

    # Validate the model
    profile = SyncProfile.model_validate(data)

    # Get time after validation
    after_validation = datetime.now(timezone.utc)

    # Check that created_at was set automatically
    assert profile.created_at is not None

    # Check that created_at is a UTC datetime
    assert profile.created_at.tzinfo == timezone.utc

    # Check that created_at is between before and after validation times
    assert before_validation <= profile.created_at <= after_validation


def test_schedule_source_url_is_serialised_as_string():
    """
    Tests that ScheduleSource.url is serialised as a string, for Firestore compatibility.
    """
    schedule_source = ScheduleSource(url=HttpUrl("https://example.com/test.ics"))

    data = schedule_source.model_dump()

    assert isinstance(data["url"], str)
    assert data["url"] == "https://example.com/test.ics"
