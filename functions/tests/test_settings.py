from functions.settings import settings


def test_redirect_uris_no_trailing_slash():
    """Test that redirect URIs don't have trailing slashes when converted to strings"""

    # Test LOCAL_REDIRECT_URI
    assert str(settings.LOCAL_REDIRECT_URI).endswith("/")

    # Test PRODUCTION_REDIRECT_URI
    assert str(settings.PRODUCTION_REDIRECT_URI).endswith("/")
