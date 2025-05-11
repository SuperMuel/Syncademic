from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, EmailStr, NaiveDatetime, field_validator


class BackendAuthorization(BaseModel):
    """
    Represents a user's backend authorization document for a calendar provider.

    Fields:
    - userId: the Firebase Auth user ID
    - provider: e.g. 'google'
    - providerAccountId: e.g. Google user ID
    - providerAccountEmail: email associated with the provider account
    - accessToken: current OAuth access token
    - refreshToken: optional OAuth refresh token
    - expirationDate: token expiration time
    """

    userId: str
    provider: Literal["google"] = "google"

    @field_validator("provider", mode="before")
    @classmethod
    def _validate_provider(cls, v: str) -> str:
        return v.lower()

    providerAccountId: str

    providerAccountEmail: EmailStr

    accessToken: str
    refreshToken: str | None = None

    # We require a naive because the OAuth token exchange library uses naive datetimes
    expirationDate: NaiveDatetime | None = None

    @field_validator("expirationDate", mode="before")
    @classmethod
    def _validate_expiration_date(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return None
        if v.tzinfo is not None:
            # Convert to UTC first, then remove timezone
            return v.astimezone(timezone.utc).replace(tzinfo=None)
        return v
