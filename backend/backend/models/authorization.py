from datetime import datetime, timezone
from typing import Literal

from pydantic import EmailStr, NaiveDatetime, field_validator

from backend.models.base import CamelCaseModel


class BackendAuthorization(CamelCaseModel):
    """
    Represents a user's backend authorization document for a calendar provider.

    Fields:
    - user_id: the Firebase Auth user ID
    - provider: e.g. 'google'
    - provider_account_id: e.g. Google user ID
    - provider_account_email: email associated with the provider account
    - access_token: current OAuth access token
    - refresh_token: optional OAuth refresh token
    - expiration_date: token expiration time
    """

    user_id: str
    provider: Literal["google"] = "google"

    @field_validator("provider", mode="before")
    @classmethod
    def _validate_provider(cls, v: str) -> str:
        return v.lower()

    provider_account_id: str

    provider_account_email: EmailStr

    access_token: str
    refresh_token: str | None = None

    # We require a naive because the OAuth token exchange library uses naive datetimes
    expiration_date: NaiveDatetime | None = None

    @field_validator("expiration_date", mode="before")
    @classmethod
    def _validate_expiration_date(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return None
        if v.tzinfo is not None:
            # Convert to UTC first, then remove timezone
            return v.astimezone(timezone.utc).replace(tzinfo=None)
        return v
