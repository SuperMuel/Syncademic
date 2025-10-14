from datetime import UTC, datetime
from enum import Enum
from json import loads
from typing import Any, Self

from pydantic import (
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    PastDatetime,
    field_serializer,
    field_validator,
    model_validator,
)

from backend.models.base import CamelCaseModel
from backend.models.rules import Ruleset
from backend.synchronizer.ics_source import IcsSource, UrlIcsSource


def utc_datetime_factory() -> datetime:
    return datetime.now(UTC)


class SyncProfileStatusType(str, Enum):
    NOT_STARTED = "notStarted"
    IN_PROGRESS = "inProgress"
    FAILED = "failed"
    SUCCESS = "success"
    DELETING = "deleting"
    DELETION_FAILED = "deletionFailed"

    def is_active(self) -> bool:
        """
        Determines if a sync profile in this state should be considered active
        for synchronization purposes.
        """

        match self:
            case (
                SyncProfileStatusType.NOT_STARTED
                | SyncProfileStatusType.SUCCESS
                | SyncProfileStatusType.FAILED
            ):
                return True
            case (
                SyncProfileStatusType.IN_PROGRESS
                | SyncProfileStatusType.DELETING
                | SyncProfileStatusType.DELETION_FAILED
            ):
                return False
            # Don't use a catch-all case ! We want a type error if a new status is not handled.


class SyncTrigger(str, Enum):
    """
    Enumerates the origins of the sync trigger:
    - on_create  : triggered when a new sync profile is created
    - manual     : triggered manually by the user
    - scheduled  : triggered by a cron job or scheduled function
    """

    ON_CREATE = "on_create"
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class SyncType(str, Enum):
    """
    Enumerates the type of synchronization:
    - regular : only future events are updated
    - full    : all events are refreshed
    """

    REGULAR = "regular"
    FULL = "full"


class ScheduleSource(CamelCaseModel):
    """
    Represents the source of the ICS file or schedule data.

    Example:
        url = "https://example.com/some_schedule.ics"
    """

    model_config = ConfigDict(frozen=True)

    url: HttpUrl = Field(..., description="Publicly accessible URL to the ICS file")

    @field_serializer("url")
    def _serialize_url(self, url: HttpUrl) -> str:
        """Convert HttpUrl to string for Firestore compatibility"""
        return str(url)

    def to_ics_source(self) -> IcsSource:
        """
        Converts the schedule source definition to an actual IcsSource object.
        """
        return UrlIcsSource(url=self.url)


class TargetCalendar(CamelCaseModel):
    """
    Represents the target calendar in the provider's system (e.g., Google Calendar).

    Fields:
    - id: unique calendar ID within the provider
    - title: title of the calendar, as rendered in the provider's UI
    - description: optional calendar description, as rendered in the provider's UI
    - provider_account_id: the user account that owns this calendar (e.g., Google user ID)
    - provider_account_email: the email for the calendar owner
    """

    id: str
    title: str = Field(..., min_length=1)
    description: str | None = Field(None)
    provider_account_id: str = Field(..., min_length=1)
    provider_account_email: EmailStr = Field(..., min_length=1)


class SyncProfileStatus(CamelCaseModel):
    """
    Tracks the current status of a synchronization profile.

    Fields:
    - type: the status type (inProgress, failed, success, etc.)
    - message: optional error or status message
    - sync_trigger: the trigger that initiated the sync
    - sync_type: whether the sync was regular or full
    - updated_at: timestamp of the last status update
    """

    type: SyncProfileStatusType
    message: str | None = None
    sync_trigger: SyncTrigger | None = None
    sync_type: SyncType | None = None
    updated_at: PastDatetime = Field(default_factory=utc_datetime_factory)


def _decode_ruleset_from_str(value: Any) -> Ruleset | dict | None:
    """A helper function to decode a JSON string into a Ruleset object because we
    store the object as a string in Firestore, but want to work with it as a validated object.
    """
    if not value:
        return None

    if isinstance(value, Ruleset) or isinstance(value, dict):
        return value

    if not isinstance(value, str):
        raise ValueError("Ruleset must be a JSON string")

    return Ruleset.model_validate(loads(value))


class SyncProfile(CamelCaseModel):
    """
    A Pydantic model representing a user's sync profile document in Firestore.

    Fields:
    - id: unique identifier of the sync profile
    - user_id: ID of the user who owns this profile
    - title: a human-friendly title
    - schedule_source: an ICS file URL or other config
    - target_calendar: references the user’s chosen target calendar
    - status: current status
    - ruleset: JSON-serialized AI ruleset, if any
    - ruleset_error: error string if AI ruleset generation fails
    - created_at: timestamp of creation
    - last_successful_sync: timestamp of the last successful sync
    """

    id: str = Field(
        ..., description="Unique identifier of the sync profile", min_length=1
    )
    user_id: str = Field(
        ..., description="ID of the user who owns this profile", min_length=1
    )

    title: str = Field(..., min_length=3, max_length=50)
    schedule_source: ScheduleSource
    target_calendar: TargetCalendar
    status: SyncProfileStatus

    ruleset: Ruleset | None = None
    ruleset_error: str | None = None

    created_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    last_successful_sync: PastDatetime | None = None

    @field_serializer("ruleset")
    def _serialize_ruleset_as_json_str(self, ruleset: Ruleset | None) -> str | None:
        return ruleset.model_dump_json() if ruleset else None

    @field_validator("ruleset", mode="before")
    @classmethod
    def _decode_ruleset_from_json_str(cls, value: Any) -> Any:
        return _decode_ruleset_from_str(value)

    @model_validator(mode="after")
    def validate_ruleset_and_error(self) -> Self:
        if self.ruleset is not None and self.ruleset_error is not None:
            raise ValueError("ruleset and ruleset_error cannot both be set")
        return self

    def update_ruleset(
        self, *, ruleset: Ruleset | None = None, error: str | None = None
    ) -> None:
        if ruleset and error:
            raise ValueError(
                "When updating the ruleset, either provide a new ruleset or an error, but not both."
            )
        self.ruleset = ruleset
        self.ruleset_error = error
