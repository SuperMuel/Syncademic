from typing import Annotated, Literal
from pydantic import AfterValidator, BaseModel, Field, HttpUrl

from functions.models.sync_profile import SyncType
from functions.settings import settings


class ValidateIcsUrlInput(BaseModel):
    url: HttpUrl = Field(..., description="URL to the ICS file")


class ValidateIcsUrlOutput(BaseModel):
    valid: bool = Field(..., description="Whether the URL is valid")
    nbEvents: int = Field(..., description="Number of events in the ICS file", ge=0)


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


def is_valid_redirect_uri(uri: HttpUrl) -> HttpUrl:
    # TODO : Check if this is safe
    if uri not in ALLOWED_REDIRECT_URIS:
        raise ValueError("Invalid redirect URI")
    return uri


RedirectUri = Annotated[HttpUrl, AfterValidator(is_valid_redirect_uri)]


class AuthorizeBackendInput(BaseModel):
    authCode: str = Field(
        ..., description="Authorization code from the frontend", min_length=1
    )
    redirectUri: RedirectUri = Field(
        settings.PRODUCTION_REDIRECT_URI,
        description="Redirect URI to use for the OAuth flow",
    )
    provider: Literal["google"] = Field("google", description="Provider to authorize")
    providerAccountId: str = Field(
        ..., description="ID of the provider account", min_length=1
    )