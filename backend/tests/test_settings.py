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
