from enum import Enum

from pydantic import BaseModel, Field, HttpUrl, EmailStr, PastDatetime

from datetime import UTC, datetime

from functions.models.rules import Ruleset


def utc_datetime_factory():
    return datetime.now(UTC)


class SyncProfileStatusType(str, Enum):
    IN_PROGRESS = "inProgress"
    FAILED = "failed"
    SUCCESS = "success"
    DELETING = "deleting"


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


class ScheduleSource(BaseModel):
    """
    Represents the source of the ICS file or schedule data.

    Example:
        url = "https://example.com/some_schedule.ics"
    """

    url: HttpUrl = Field(..., description="Publicly accessible URL to the ICS file")


class TargetCalendar(BaseModel):
    """
    Represents the target calendar in the provider's system (e.g., Google Calendar).

    Fields:
    - id: unique calendar ID within the provider
    - title: title of the calendar, as rendered in the provider's UI
    - description: optional calendar description, as rendered in the provider's UI
    - providerAccountId: the user account that owns this calendar (e.g., Google user ID)
    - providerAccountEmail: the email for the calendar owner
    """

    id: str
    title: str = Field(..., min_length=1)
    description: str | None = Field(None)
    providerAccountId: str = Field(..., min_length=1)
    providerAccountEmail: EmailStr = Field(..., min_length=1)


class SyncProfileStatus(BaseModel):
    """
    Tracks the current status of a synchronization profile.

    Fields:
    - type: The status type (inProgress, failed, success, etc.)
    - message: Optional error or status message
    - syncTrigger: The trigger that initiated the sync
    - syncType: Whether the sync was regular or full
    - updatedAt: Timestamp of last status update
    """

    type: SyncProfileStatusType
    message: str | None = None
    syncTrigger: SyncTrigger | None = None
    syncType: SyncType | None = None
    updatedAt: PastDatetime = Field(default_factory=utc_datetime_factory)


class SyncProfile(BaseModel):
    """
    A Pydantic model representing a user's sync profile document in Firestore.

    Fields:
    - title: a human-friendly title
    - scheduleSource: an ICS file URL or other config
    - targetCalendar: references the user’s chosen target calendar
    - status: current status
    - ruleset: JSON-serialized AI ruleset, if any
    - ruleset_error: error string if AI ruleset generation fails
    - created_at: timestamp of creation
    - lastSuccessfulSync: timestamp of last successful sync
    """

    title: str = Field(..., min_length=3, max_length=50)
    scheduleSource: ScheduleSource
    targetCalendar: TargetCalendar
    status: SyncProfileStatus

    ruleset: Ruleset | None = None
    ruleset_error: str | None = None

    created_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    lastSuccessfulSync: PastDatetime | None = None
