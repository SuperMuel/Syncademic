import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from functions.models import BackendAuthorization


def test_backend_authorization_minimal():
    """
    Test creating a minimal valid BackendAuthorization object.
    """
    auth = BackendAuthorization(
        userId="someFirebaseUID",
        providerAccountId="1234567890",
        providerAccountEmail="user@example.com",
        accessToken="abc123",
    )
    assert auth.provider == "google"
    assert auth.expirationDate is None


@pytest.mark.parametrize("provider", ["Google", "google", "GOOGLE", "gOOgle"])
def test_backend_authorization_with_provider(provider):
    auth = BackendAuthorization(
        userId="someFirebaseUID",
        provider=provider,
        providerAccountId="1234567890",
        providerAccountEmail="user@example.com",
        accessToken="abc123",
    )

    assert auth.provider == "google"


def test_backend_authorization_with_invalid_provider():
    with pytest.raises(ValidationError):
        BackendAuthorization(
            userId="someFirebaseUID",
            provider="invalid",  # type: ignore
            providerAccountId="1234567890",
            providerAccountEmail="user@example.com",
            accessToken="abc123",
        )


def test_backend_authorization_with_aware_expiration():
    """
    Test creating an authorization object with an expiration date.
    """
    now_utc = datetime.now(timezone.utc)
    auth = BackendAuthorization(
        userId="someFirebaseUID",
        providerAccountId="myGoogleId",
        providerAccountEmail="user@example.com",
        accessToken="token123",
        refreshToken="refreshXYZ",
        expirationDate=now_utc,
    )

    # Should be converted to naive
    assert auth.expirationDate == now_utc.replace(tzinfo=None)
    assert auth.refreshToken == "refreshXYZ"


def test_backend_authorization_with_naive_expiration():
    now_utc = datetime.now()
    auth = BackendAuthorization(
        userId="someFirebaseUID",
        providerAccountId="myGoogleId",
        providerAccountEmail="user@example.com",
        accessToken="token123",
        refreshToken="refreshXYZ",
        expirationDate=now_utc,
    )


def test_backend_authorization_invalid_email():
    """
    Test that providing an invalid email raises a ValidationError.
    """
    with pytest.raises(ValidationError) as exc_info:
        BackendAuthorization(
            userId="user1",
            providerAccountId="gId",
            providerAccountEmail="invalid-email",
            accessToken="token",
        )
    assert "value is not a valid email address" in str(exc_info.value)
