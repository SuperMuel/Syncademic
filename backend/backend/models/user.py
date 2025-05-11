from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class UserProviderData(BaseModel):
    """Model representing user authentication provider data."""

    provider_id: str
    uid: str
    email: str | None = None
    display_name: str | None = None


class UserMetadata(BaseModel):
    """Model representing user metadata."""

    creation_timestamp: datetime | None = None
    last_sign_in_timestamp: datetime | None = None


class User(BaseModel):
    """Model representing a Firebase user."""

    uid: str
    email: str | None = None
    display_name: str | None = None
    disabled: bool = False
    email_verified: bool = False
    provider_data: list[UserProviderData] = Field(default_factory=list)
    custom_claims: dict[str, Any] | None = None
    user_metadata: UserMetadata = Field(default_factory=UserMetadata)
