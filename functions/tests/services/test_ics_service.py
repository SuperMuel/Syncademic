from unittest.mock import Mock
import pytest
from pydantic import HttpUrl
import arrow

from functions.models.schemas import ValidateIcsUrlOutput
from functions.services.ics_service import IcsService
from functions.shared.event import Event


@pytest.fixture
def mock_events() -> list[Event]:
    now = arrow.now()
    return [
        Event(start=now, end=now.shift(hours=1), title="Event 1"),
        Event(start=now.shift(days=1), end=now.shift(days=1, hours=2), title="Event 2"),
    ]


@pytest.fixture
def mock_ics_parser() -> Mock:
    return Mock()


@pytest.fixture
def mock_ics_storage() -> Mock:
    return Mock()


@pytest.fixture
def mock_url_ics_source() -> Mock:
    return Mock()


@pytest.fixture
def service(mock_ics_parser: Mock, mock_ics_storage: Mock) -> IcsService:
    return IcsService(
        ics_parser=mock_ics_parser,
        ics_storage=mock_ics_storage,
    )


def test_validate_ics_url_success(
    service: IcsService,
    mock_ics_parser: Mock,
    mock_ics_storage: Mock,
    mock_url_ics_source: Mock,
    mock_events: list[Event],
) -> None:
    # Arrange
    test_url = "https://example.com/calendar.ics"
    test_ics_content = "test_ics_content"

    mock_url_ics_source.get_ics_string.return_value = test_ics_content
    mock_url_ics_source.url = test_url
    mock_ics_parser.parse.return_value = mock_events

    # Act
    result = service.validate_ics_url(mock_url_ics_source)

    # Assert
    assert isinstance(result, ValidateIcsUrlOutput)
    assert result.valid is True
    assert result.error is None
    assert result.nbEvents == len(mock_events)

    mock_url_ics_source.get_ics_string.assert_called_once()
    mock_ics_parser.parse.assert_called_once_with(ics_str=test_ics_content)
    mock_ics_storage.save_to_cache.assert_called_once_with(
        ics_source=mock_url_ics_source,
        ics_str=test_ics_content,
        parsing_error=None,
    )


def test_validate_ics_url_fetch_failure(
    service: IcsService,
    mock_url_ics_source: Mock,
) -> None:
    fetch_error = Exception("Network error")
    # Arrange
    mock_url_ics_source.get_ics_string.side_effect = fetch_error

    # Act
    result = service.validate_ics_url(mock_url_ics_source)

    # Assert
    assert isinstance(result, ValidateIcsUrlOutput)
    assert result.valid is False
    assert str(fetch_error) in str(result.error)
    assert result.nbEvents is None


def test_validate_ics_url_parse_failure(
    service: IcsService,
    mock_ics_parser: Mock,
    mock_ics_storage: Mock,
    mock_url_ics_source: Mock,
) -> None:
    # Arrange
    test_url = "https://example.com/calendar.ics"
    test_ics_content = "invalid_ics_content"
    parse_error = Exception("Invalid ICS format")

    mock_url_ics_source.get_ics_string.return_value = test_ics_content
    mock_url_ics_source.url = test_url
    mock_ics_parser.parse.side_effect = parse_error

    # Act
    result = service.validate_ics_url(mock_url_ics_source)

    # Assert
    assert isinstance(result, ValidateIcsUrlOutput)
    assert result.valid is False
    assert str(parse_error) in str(result.error)
    assert result.nbEvents is None
    mock_ics_storage.save_to_cache.assert_called_once_with(
        ics_source=mock_url_ics_source,
        ics_str=test_ics_content,
        parsing_error=parse_error,
    )


def test_validate_ics_url_no_storage(
    mock_ics_parser: Mock,
    mock_url_ics_source: Mock,
    mock_events: list[Event],
) -> None:
    # Arrange
    service = IcsService(ics_parser=mock_ics_parser, ics_storage=None)
    test_ics_content = "test_ics_content"

    mock_url_ics_source.get_ics_string.return_value = test_ics_content
    mock_ics_parser.parse.return_value = mock_events

    # Act
    result = service.validate_ics_url(mock_url_ics_source)

    # Assert
    assert isinstance(result, ValidateIcsUrlOutput)
    assert result.valid is True
    assert result.error is None
    assert result.nbEvents == len(mock_events)


def test_validate_ics_url_storage_failure(
    service: IcsService,
    mock_ics_parser: Mock,
    mock_ics_storage: Mock,
    mock_url_ics_source: Mock,
    mock_events: list[Event],
) -> None:
    # Arrange
    test_url = "https://example.com/calendar.ics"
    test_ics_content = "test_ics_content"

    mock_url_ics_source.get_ics_string.return_value = test_ics_content
    mock_url_ics_source.url = test_url
    mock_ics_parser.parse.return_value = mock_events
    mock_ics_storage.save_to_cache.side_effect = Exception("Storage error")

    # Act
    result = service.validate_ics_url(mock_url_ics_source)

    # Assert
    assert isinstance(result, ValidateIcsUrlOutput)
    assert result.valid is True
    assert result.error is None
    assert result.nbEvents == len(mock_events)


def test_validate_ics_url_with_http_url(
    service: IcsService,
    mock_ics_parser: Mock,
    mock_url_ics_source: Mock,
    mock_events: list[Event],
) -> None:
    # Arrange
    test_url = HttpUrl("https://example.com/calendar.ics")
    test_ics_content = "test_ics_content"

    mock_url_ics_source.get_ics_string.return_value = test_ics_content
    mock_url_ics_source.url = test_url
    mock_ics_parser.parse.return_value = mock_events

    # Act
    result = service.validate_ics_url(mock_url_ics_source)

    # Assert
    assert isinstance(result, ValidateIcsUrlOutput)
    assert result.valid is True
    assert result.error is None
    assert result.nbEvents == len(mock_events)
