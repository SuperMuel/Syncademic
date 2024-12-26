from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr


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
    providerAccountId: str

    providerAccountEmail: EmailStr

    accessToken: str
    refreshToken: str | None = None
    expirationDate: datetime | None = None
