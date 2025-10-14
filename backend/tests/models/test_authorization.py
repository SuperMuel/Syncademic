import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from backend.models import BackendAuthorization


def test_backend_authorization_minimal():
    """
    Test creating a minimal valid BackendAuthorization object.
    """
    auth = BackendAuthorization(
        user_id="someFirebaseUID",
        provider_account_id="1234567890",
        provider_account_email="user@example.com",
        access_token="abc123",
    )
    assert auth.provider == "google"
    assert auth.expiration_date is None


@pytest.mark.parametrize("provider", ["Google", "google", "GOOGLE", "gOOgle"])
def test_backend_authorization_with_provider(provider):
    auth = BackendAuthorization(
        user_id="someFirebaseUID",
        provider=provider,
        provider_account_id="1234567890",
        provider_account_email="user@example.com",
        access_token="abc123",
    )

    assert auth.provider == "google"


def test_backend_authorization_with_invalid_provider():
    with pytest.raises(ValidationError):
        BackendAuthorization(
            user_id="someFirebaseUID",
            provider="invalid",  # type: ignore
            provider_account_id="1234567890",
            provider_account_email="user@example.com",
            access_token="abc123",
        )


def test_backend_authorization_with_aware_expiration():
    """
    Test creating an authorization object with an expiration date.
    """
    now_utc = datetime.now(timezone.utc)
    auth = BackendAuthorization(
        user_id="someFirebaseUID",
        provider_account_id="myGoogleId",
        provider_account_email="user@example.com",
        access_token="token123",
        refresh_token="refreshXYZ",
        expiration_date=now_utc,
    )

    # Should be converted to naive
    assert auth.expiration_date == now_utc.replace(tzinfo=None)
    assert auth.refresh_token == "refreshXYZ"


def test_backend_authorization_with_naive_expiration():
    now_utc = datetime.now()
    auth = BackendAuthorization(
        user_id="someFirebaseUID",
        provider_account_id="myGoogleId",
        provider_account_email="user@example.com",
        access_token="token123",
        refresh_token="refreshXYZ",
        expiration_date=now_utc,
    )


def test_backend_authorization_invalid_email():
    """
    Test that providing an invalid email raises a ValidationError.
    """
    with pytest.raises(ValidationError) as exc_info:
        BackendAuthorization(
            user_id="user1",
            provider_account_id="gId",
            provider_account_email="invalid-email",
            access_token="token",
        )
    assert "value is not a valid email address" in str(exc_info.value)
