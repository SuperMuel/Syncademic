from pydantic import ValidationError
import pytest
from backend.settings import settings, Settings


def test_redirect_uris_no_trailing_slash():
    """Test that redirect URIs don't have trailing slashes when converted to strings"""

    # Test LOCAL_REDIRECT_URI
    assert not str(settings.LOCAL_REDIRECT_URI).endswith("/")

    # Test PRODUCTION_REDIRECT_URI
    assert not str(settings.PRODUCTION_REDIRECT_URI).endswith("/")


def test_invalid_redirect_uri_local():
    with pytest.raises(ValidationError):
        Settings(LOCAL_REDIRECT_URI="oijfezoifjez")  # type: ignore


def test_invalid_redirect_uri_production():
    with pytest.raises(ValidationError):
        Settings(PRODUCTION_REDIRECT_URI="oijfezoifjez")  # type: ignore


def test_storage_bucket_read_from_storage_bucket_env(monkeypatch):
    # Firebase rejects FIREBASE_-prefixed keys in deployed .env files.
    monkeypatch.delenv("FIREBASE_STORAGE_BUCKET", raising=False)
    monkeypatch.setenv("STORAGE_BUCKET", "bucket-from-dotenv")

    assert Settings().FIREBASE_STORAGE_BUCKET == "bucket-from-dotenv"


def test_storage_bucket_still_read_from_legacy_env(monkeypatch):
    monkeypatch.delenv("STORAGE_BUCKET", raising=False)
    monkeypatch.setenv("FIREBASE_STORAGE_BUCKET", "legacy-bucket")

    assert Settings().FIREBASE_STORAGE_BUCKET == "legacy-bucket"
