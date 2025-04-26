from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, Field, HttpUrl, field_validator

from functions.models.sync_profile import ScheduleSource, SyncType, TargetCalendar
from functions.settings import RedirectUri, settings


class ValidateIcsUrlInput(BaseModel):
    url: str = Field(..., description="URL to the ICS file")


class ValidateIcsUrlOutput(BaseModel):
    valid: bool = Field(..., description="Whether the URL is valid")
    nbEvents: int | None = Field(
        default=None, description="Number of events in the ICS file", ge=0
    )
    error: str | None = Field(
        None,
        description="Error message if the URL is not valid",
    )

    # Maybe we'd like to return the parsed events to the frontend


class ListUserCalendarsInput(BaseModel):
    providerAccountId: str = Field(
        ..., description="ID of the provider account", min_length=1
    )


class IsAuthorizedInput(BaseModel):
    providerAccountId: str = Field(
        ..., description="ID of the provider account", min_length=1
    )


class IsAuthorizedOutput(BaseModel):
    authorized: bool = Field(..., description="Whether the user is authorized")


class CreateNewCalendarInput(BaseModel):
    providerAccountId: str = Field(
        ..., description="ID of the provider account", min_length=1
    )
    colorId: int | None = Field(
        None,
        description="ID of the color to use for the calendar, corresponding to the Google Calendar API colors",
        ge=1,
        le=25,
    )

    summary: str = Field(..., description="Name of the calendar", min_length=1)
    description: str = Field("", description="Description of the calendar")


class RequestSyncInput(BaseModel):
    syncProfileId: str = Field(
        ..., description="ID of the sync profile to use", min_length=1
    )
    syncType: SyncType = Field(SyncType.REGULAR, description="Type of sync to perform")


class DeleteSyncProfileInput(BaseModel):
    syncProfileId: str = Field(
        ..., description="ID of the sync profile to delete", min_length=1
    )


ALLOWED_REDIRECT_URIS = [settings.LOCAL_REDIRECT_URI, settings.PRODUCTION_REDIRECT_URI]


class AuthorizeBackendInput(BaseModel):
    authCode: str = Field(
        ..., description="Authorization code from the frontend", min_length=1
    )
    redirectUri: RedirectUri = Field(
        settings.PRODUCTION_REDIRECT_URI,
        description="Redirect URI to use for the OAuth flow",
    )
    provider: Literal["google"] = Field("google", description="Provider to authorize")

    @field_validator("provider", mode="before")
    @classmethod
    def _validate_provider(cls, v: str) -> str:
        return v.lower()

    @field_validator("redirectUri")
    @classmethod
    def _validate_redirect_uri(cls, uri: HttpUrl) -> HttpUrl:
        """Validate that the redirect URI is allowed"""
        if uri not in ALLOWED_REDIRECT_URIS:
            raise ValueError(f"Invalid redirect URI: `{uri}`")
        return uri

    providerAccountId: str = Field(
        ..., description="ID of the provider account", min_length=1
    )


class CreateNewTargetCalendarInput(BaseModel):
    """Specifies details for creating a new target calendar during sync profile creation."""

    type: Literal["createNew"]
    colorId: int | None = Field(
        None,
        description="Optional color ID for the new calendar (1-25).",
        ge=1,
        le=25,
    )
    providerAccountId: str = Field(
        ..., description="ID of the provider account", min_length=1
    )


class UseExistingTargetCalendarInput(BaseModel):
    """Specifies details for using an existing target calendar during sync profile creation."""

    type: Literal["useExisting"]
    calendarId: str = Field(
        ..., description="ID of the existing calendar", min_length=1
    )
    providerAccountId: str = Field(
        ..., description="ID of the provider account", min_length=1
    )


class CreateSyncProfileInput(BaseModel):
    title: str = Field(
        ...,
        description="User-defined title for the sync profile.",
        min_length=3,
        max_length=50,
        examples=["My University Schedule", "Master IF Semestre 1"],
    )

    scheduleSource: ScheduleSource
    targetCalendar: CreateNewTargetCalendarInput | UseExistingTargetCalendarInput = (
        Field(
            ...,
            discriminator="type",
        )
    )
