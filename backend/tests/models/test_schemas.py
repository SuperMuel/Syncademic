import pytest
from pydantic import HttpUrl, ValidationError

from backend.models.schemas import (
    AuthorizeBackendInput,
    CreateNewCalendarInput,
    DeleteSyncProfileInput,
    IsAuthorizedInput,
    IsAuthorizedOutput,
    ListUserCalendarsInput,
    RequestSyncInput,
    ValidateIcsUrlInput,
    ValidateIcsUrlOutput,
)
from backend.models.sync_profile import SyncType
from backend.settings import settings


@pytest.mark.parametrize(
    "scheme",
    ["http", "https", "webcal"],
)
def test_validate_ics_url_input_valid(scheme: str):
    """Ensure ValidateIcsUrlInput works with a valid ICS URL."""
    data = {"url": f"{scheme}://example.com/calendar.ics"}
    obj = ValidateIcsUrlInput.model_validate(data)
    assert str(obj.url) == f"{scheme}://example.com/calendar.ics"


def test_validate_ics_url_output_valid_minimum():
    """Test ValidateIcsUrlOutput with minimum valid values."""
    data = {"valid": True, "nbEvents": 0}
    output = ValidateIcsUrlOutput.model_validate(data)
    assert output.valid is True
    assert output.nbEvents == 0


def test_validate_ics_url_output_valid_with_events():
    """Test ValidateIcsUrlOutput with positive number of events."""
    data = {"valid": False, "nbEvents": 42}
    output = ValidateIcsUrlOutput.model_validate(data)
    assert output.valid is False
    assert output.nbEvents == 42


def test_validate_ics_url_output_negative_events():
    """Test ValidateIcsUrlOutput fails with negative number of events."""
    with pytest.raises(ValidationError) as exc_info:
        ValidateIcsUrlOutput.model_validate({"valid": True, "nbEvents": -1})
    assert "Input should be greater than or equal to 0" in str(exc_info.value)


def test_validate_ics_url_output_invalid_types():
    """Test ValidateIcsUrlOutput fails with invalid field types."""
    with pytest.raises(ValidationError) as exc_info:
        ValidateIcsUrlOutput.model_validate(
            {"valid": "not_a_bool", "nbEvents": "not_an_int"}
        )
    error_str = str(exc_info.value)
    assert "valid" in error_str
    assert "nbEvents" in error_str


def test_list_user_calendars_input_valid():
    """Ensure ListUserCalendarsInput works with a valid providerAccountId."""
    data = {"providerAccountId": "1234567890"}
    obj = ListUserCalendarsInput.model_validate(data)
    assert obj.providerAccountId == "1234567890"


def test_list_user_calendars_input_invalid():
    """Ensure ListUserCalendarsInput fails if providerAccountId is empty."""
    data = {"providerAccountId": ""}
    with pytest.raises(ValidationError):
        ListUserCalendarsInput(**data)


def test_is_authorized_input_valid():
    """Check that IsAuthorizedInput accepts a valid non-empty providerAccountId."""
    data = {"providerAccountId": "google_id_123"}
    obj = IsAuthorizedInput.model_validate(data)
    assert obj.providerAccountId == "google_id_123"


def test_is_authorized_input_empty_provider_id():
    """Test IsAuthorizedInput fails with empty providerAccountId."""
    with pytest.raises(ValidationError):
        IsAuthorizedInput.model_validate({"providerAccountId": ""})


def test_is_authorized_output_valid():
    """Check that IsAuthorizedOutput can be created with valid data."""
    IsAuthorizedOutput(authorized=True)


def test_create_new_calendar_input_valid():
    """Check that CreateNewCalendarInput validates correctly with valid data."""
    data = {
        "providerAccountId": "google_id_123",
        "colorId": 10,
        "summary": "My New Calendar",
        "description": "A calendar created for testing.",
    }
    obj = CreateNewCalendarInput.model_validate(data)
    assert obj.providerAccountId == "google_id_123"
    assert obj.colorId == 10
    assert obj.summary == "My New Calendar"
    assert obj.description == "A calendar created for testing."


def test_create_new_calendar_input_valid_no_description():
    """Check that CreateNewCalendarInput validates correctly with valid data."""
    data = {
        "providerAccountId": "google_id_123",
        "colorId": 10,
        "summary": "My New Calendar",
    }
    obj = CreateNewCalendarInput.model_validate(data)
    assert obj.providerAccountId == "google_id_123"
    assert obj.colorId == 10
    assert obj.summary == "My New Calendar"
    assert obj.description == ""


def test_create_new_calendar_input_invalid_no_provider_account_id():
    """Ensure CreateNewCalendarInput fails if providerAccountId is empty."""
    data = {
        "providerAccountId": "",
        "colorId": 10,
        "summary": "My New Calendar",
        "description": "A calendar created for testing.",
    }
    with pytest.raises(ValidationError) as exc_info:
        CreateNewCalendarInput(**data)
    assert "String should have at least 1 character" in str(exc_info.value)


def test_create_new_calendar_input_invalid_no_summary():
    """Ensure CreateNewCalendarInput fails if summary is empty."""
    data = {
        "providerAccountId": "google_id_123",
        "colorId": 10,
        "summary": "",
        "description": "A calendar created for testing.",
    }
    with pytest.raises(ValidationError) as exc_info:
        CreateNewCalendarInput(**data)
    assert "String should have at least 1 character" in str(exc_info.value)


def test_create_new_calendar_input_invalid_color():
    """Ensure CreateNewCalendarInput fails if colorId is out of the allowed range (1-25)."""
    data = {
        "providerAccountId": "google_id_123",
        "colorId": 50,
        "summary": "Calendar Title",
        "description": "Test",
    }
    with pytest.raises(ValidationError) as exc_info:
        CreateNewCalendarInput(**data)
    assert "Input should be less than or equal to 25" in str(exc_info.value)


def test_request_sync_input_valid():
    """Check that RequestSyncInput validates with valid data."""
    data = {"syncProfileId": "profile_123", "syncType": "regular"}
    obj = RequestSyncInput.model_validate(data)
    assert obj.syncProfileId == "profile_123"
    assert obj.syncType == SyncType.REGULAR


def test_request_sync_input_invalid_sync_type():
    """Ensure RequestSyncInput fails if syncType is not recognized."""
    data = {"syncProfileId": "profile_123", "syncType": "invalid_sync_type"}
    with pytest.raises(ValidationError) as exc_info:
        RequestSyncInput.model_validate(data)
    assert "1 validation error for RequestSyncInput\nsyncType" in str(exc_info.value)


def test_delete_sync_profile_input_valid():
    """Check that DeleteSyncProfileInput validates with valid data."""
    data = {"syncProfileId": "profile_to_delete"}
    obj = DeleteSyncProfileInput(**data)
    assert obj.syncProfileId == "profile_to_delete"


def test_delete_sync_profile_input_empty_id():
    """Ensure DeleteSyncProfileInput fails if syncProfileId is empty."""
    data = {"syncProfileId": ""}
    with pytest.raises(ValidationError) as exc_info:
        DeleteSyncProfileInput(**data)
    assert "1 validation error for DeleteSyncProfileInput\nsyncProfileId" in str(
        exc_info.value
    )


@pytest.mark.parametrize(
    "redirect_uri",
    [
        settings.PRODUCTION_REDIRECT_URI,
        settings.LOCAL_REDIRECT_URI,
    ],
)
def test_authorize_backend_input_valid(redirect_uri: HttpUrl):
    """Ensure AuthorizeBackendInput validates with correct data."""
    data = {
        "authCode": "some-code-value",
        "redirectUri": redirect_uri,
        "provider": "google",
        "providerAccountId": "1122334455",
    }
    obj = AuthorizeBackendInput.model_validate(data)
    assert obj.authCode == "some-code-value"
    assert obj.redirectUri == redirect_uri
    assert obj.provider == "google"
    assert obj.providerAccountId == "1122334455"


def test_authorize_backend_input_missing_auth_code():
    """Ensure AuthorizeBackendInput fails if authCode is missing."""
    data = {
        "redirectUri": settings.PRODUCTION_REDIRECT_URI,
        "provider": "google",
        "providerAccountId": "1122334455",
    }
    with pytest.raises(ValidationError) as exc_info:
        AuthorizeBackendInput(**data)
    assert "1 validation error for AuthorizeBackendInput\nauthCode" in str(
        exc_info.value
    )


def test_authorize_backend_input_unknown_redirect_uri():
    """Ensure AuthorizeBackendInput fails if redirectUri is not known.
    (It should be either LOCAL_REDIRECT_URI or PRODUCTION_REDIRECT_URI.)
    """
    data = {
        "authCode": "some-code-value",
        "redirectUri": "https://example.com/redirect",
        "provider": "google",
        "providerAccountId": "1122334455",
    }
    with pytest.raises(ValidationError) as exc_info:
        AuthorizeBackendInput.model_validate(data)
    assert "Invalid redirect URI" in str(exc_info.value)


def test_authorize_backend_input_redirect_uri_no_trailing_slash():
    """Test that the string serialization of redirectUri doesn't have a trailing slash."""
    data = {
        "authCode": "some-code-value",
        "redirectUri": settings.PRODUCTION_REDIRECT_URI,
        "provider": "google",
        "providerAccountId": "1122334455",
    }
    obj = AuthorizeBackendInput.model_validate(data)
    assert not str(obj.redirectUri).endswith("/")
