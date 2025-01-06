import pytest
from datetime import datetime, timezone
from pydantic import ValidationError, HttpUrl
from functions.models import (
    SyncProfile,
    SyncProfileStatus,
    SyncProfileStatusType,
    ScheduleSource,
    TargetCalendar,
    SyncTrigger,
    SyncType,
)
from functions.models.rules import (
    Rule,
    Ruleset,
    TextFieldCondition,
    ChangeColorAction,
    GoogleEventColor,
)

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


VALID_RULESET = Ruleset(
    rules=[
        Rule(
            condition=TextFieldCondition(
                field="title",
                operator="contains",
                value="x",
            ),
            actions=[ChangeColorAction(value=GoogleEventColor.BASIL)],
        )
    ],
)


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
