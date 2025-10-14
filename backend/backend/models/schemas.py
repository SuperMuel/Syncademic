from typing import Literal

from pydantic import Field, HttpUrl, field_validator

from backend.models.base import CamelCaseModel
from backend.models.sync_profile import ScheduleSource, SyncType
from backend.settings import RedirectUri, settings


class ValidateIcsUrlInput(CamelCaseModel):
    url: str = Field(..., description="URL to the ICS file")


class ValidateIcsUrlOutput(CamelCaseModel):
    valid: bool = Field(..., description="Whether the URL is valid")
    nb_events: int | None = Field(
        default=None, description="Number of events in the ICS file", ge=0
    )
    error: str | None = Field(
        None,
        description="Error message if the URL is not valid",
    )

    # Maybe we'd like to return the parsed events to the frontend


class ListUserCalendarsInput(CamelCaseModel):
    provider_account_id: str = Field(
        ..., description="ID of the provider account", min_length=1
    )


class IsAuthorizedInput(CamelCaseModel):
    provider_account_id: str = Field(
        ..., description="ID of the provider account", min_length=1
    )


class IsAuthorizedOutput(CamelCaseModel):
    authorized: bool = Field(..., description="Whether the user is authorized")


class CreateNewCalendarInput(CamelCaseModel):
    provider_account_id: str = Field(
        ..., description="ID of the provider account", min_length=1
    )
    color_id: int | None = Field(
        None,
        description="ID of the color to use for the calendar, corresponding to the Google Calendar API colors",
        ge=1,
        le=25,
    )

    summary: str = Field(..., description="Name of the calendar", min_length=1)
    description: str = Field("", description="Description of the calendar")


class RequestSyncInput(CamelCaseModel):
    sync_profile_id: str = Field(
        ..., description="ID of the sync profile to use", min_length=1
    )
    sync_type: SyncType = Field(SyncType.REGULAR, description="Type of sync to perform")


class DeleteSyncProfileInput(CamelCaseModel):
    sync_profile_id: str = Field(
        ..., description="ID of the sync profile to delete", min_length=1
    )


ALLOWED_REDIRECT_URIS = [settings.LOCAL_REDIRECT_URI, settings.PRODUCTION_REDIRECT_URI]


class AuthorizeBackendInput(CamelCaseModel):
    auth_code: str = Field(
        ..., description="Authorization code from the frontend", min_length=1
    )
    redirect_uri: RedirectUri = Field(
        settings.PRODUCTION_REDIRECT_URI,
        description="Redirect URI to use for the OAuth flow",
    )
    provider: Literal["google"] = Field("google", description="Provider to authorize")

    @field_validator("provider", mode="before")
    @classmethod
    def _validate_provider(cls, v: str) -> str:
        return v.lower()

    @field_validator("redirect_uri")
    @classmethod
    def _validate_redirect_uri(cls, uri: HttpUrl) -> HttpUrl:
        """Validate that the redirect URI is allowed"""
        if uri not in ALLOWED_REDIRECT_URIS:
            raise ValueError(f"Invalid redirect URI: `{uri}`")
        return uri

    provider_account_id: str = Field(
        ..., description="ID of the provider account", min_length=1
    )


class CreateNewTargetCalendarInput(CamelCaseModel):
    """Specifies details for creating a new target calendar during sync profile creation."""

    type: Literal["createNew"]
    color_id: int | None = Field(
        None,
        description="Optional color ID for the new calendar (1-25).",
        ge=1,
        le=25,
    )

    @field_validator("color_id", mode="before")
    @classmethod
    def _validate_color_id(cls, v: str | int | None) -> int | None:
        if v is None:
            return None
        if isinstance(v, str):
            return int(v)  # Allow string input for colorId (e.g. "1" instead of 1)
        return v

    provider_account_id: str = Field(
        ..., description="ID of the provider account", min_length=1
    )


class UseExistingTargetCalendarInput(CamelCaseModel):
    """Specifies details for using an existing target calendar during sync profile creation."""

    type: Literal["useExisting"]
    calendar_id: str = Field(
        ..., description="ID of the existing calendar", min_length=1
    )
    provider_account_id: str = Field(
        ..., description="ID of the provider account", min_length=1
    )


class CreateSyncProfileInput(CamelCaseModel):
    title: str = Field(
        ...,
        description="User-defined title for the sync profile.",
        min_length=3,
        max_length=50,
        examples=["My University Schedule", "Master IF Semestre 1"],
    )

    schedule_source: ScheduleSource
    target_calendar: CreateNewTargetCalendarInput | UseExistingTargetCalendarInput = (
        Field(
            ...,
            discriminator="type",
        )
    )
