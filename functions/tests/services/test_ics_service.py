from unittest.mock import Mock

import arrow
import pytest
from pydantic import HttpUrl

from functions.models.schemas import ValidateIcsUrlOutput
from functions.services.exceptions.ics import IcsParsingError, IcsSourceError
from functions.services.ics_service import IcsService
from functions.shared.event import Event
from functions.synchronizer.ics_parser import IcsParser
from functions.synchronizer.ics_source import UrlIcsSource


@pytest.fixture
def mock_events() -> list[Event]:
    now = arrow.now()
    return [
        Event(start=now, end=now.shift(hours=1), title="Event 1"),
        Event(start=now.shift(days=1), end=now.shift(days=1, hours=2), title="Event 2"),
    ]


@pytest.fixture
def mock_ics_source() -> Mock:
    return Mock(spec=UrlIcsSource)


@pytest.fixture
def mock_ics_parser() -> Mock:
    return Mock(spec=IcsParser)


@pytest.fixture
def mock_ics_storage() -> Mock:
    return Mock()


@pytest.fixture
def mock_url_ics_source() -> Mock:
    return Mock(spec=UrlIcsSource)


@pytest.fixture
def service(mock_ics_parser: Mock, mock_ics_storage: Mock) -> IcsService:
    return IcsService(
        ics_parser=mock_ics_parser,
        ics_storage=mock_ics_storage,
    )


class TestTryFetchAndParse:
    def test_successful_fetch_and_parse(
        self,
        service: IcsService,
        mock_ics_source: Mock,
        mock_ics_parser: Mock,
        mock_ics_storage: Mock,
    ) -> None:
        # Arrange
        ics_content = "BEGIN:VCALENDAR..."
        expected_events = [Mock(spec=Event), Mock(spec=Event)]
        mock_ics_source.get_ics_string.return_value = ics_content
        mock_ics_parser.try_parse.return_value = expected_events

        # Act
        result = service.try_fetch_and_parse(mock_ics_source)

        # Assert
        assert result == expected_events
        mock_ics_source.get_ics_string.assert_called_once()
        mock_ics_parser.try_parse.assert_called_once_with(ics_content)
        mock_ics_storage.save_to_cache.assert_called_once_with(
            ics_source=mock_ics_source,
            ics_str=ics_content,
            parsing_error=None,
        )

    def test_fetch_error(
        self,
        service: IcsService,
        mock_ics_source: Mock,
        mock_ics_parser: Mock,
        mock_ics_storage: Mock,
    ) -> None:
        # Arrange
        error = IcsSourceError("Failed to fetch")
        mock_ics_source.get_ics_string.side_effect = error

        # Act
        result = service.try_fetch_and_parse(mock_ics_source)

        # Assert
        assert result == error
        mock_ics_source.get_ics_string.assert_called_once()
        mock_ics_parser.try_parse.assert_not_called()
        mock_ics_storage.save_to_cache.assert_not_called()

    def test_parse_error(
        self,
        service: IcsService,
        mock_ics_source: Mock,
        mock_ics_parser: Mock,
        mock_ics_storage: Mock,
    ) -> None:
        # Arrange
        ics_content = "BEGIN:VCALENDAR..."
        error = IcsParsingError("Invalid format")
        mock_ics_source.get_ics_string.return_value = ics_content
        mock_ics_parser.try_parse.return_value = error

        # Act
        result = service.try_fetch_and_parse(mock_ics_source)

        # Assert
        assert result == error
        mock_ics_source.get_ics_string.assert_called_once()
        mock_ics_parser.try_parse.assert_called_once_with(ics_content)
        mock_ics_storage.save_to_cache.assert_called_once_with(
            ics_source=mock_ics_source,
            ics_str=ics_content,
            parsing_error=error,
        )

    def test_storage_disabled(
        self,
        service: IcsService,
        mock_ics_source: Mock,
        mock_ics_parser: Mock,
        mock_ics_storage: Mock,
    ) -> None:
        # Arrange
        ics_content = "BEGIN:VCALENDAR..."
        expected_events = [Mock(spec=Event)]
        mock_ics_source.get_ics_string.return_value = ics_content
        mock_ics_parser.try_parse.return_value = expected_events

        # Act
        result = service.try_fetch_and_parse(mock_ics_source, save_to_storage=False)

        # Assert
        assert result == expected_events
        mock_ics_storage.save_to_cache.assert_not_called()

    def test_storage_error_handled(
        self,
        service: IcsService,
        mock_ics_source: Mock,
        mock_ics_parser: Mock,
        mock_ics_storage: Mock,
    ) -> None:
        # Arrange
        ics_content = "BEGIN:VCALENDAR..."
        expected_events = [Mock(spec=Event)]
        mock_ics_source.get_ics_string.return_value = ics_content
        mock_ics_parser.try_parse.return_value = expected_events
        mock_ics_storage.save_to_cache.side_effect = Exception("Storage error")

        # Act
        result = service.try_fetch_and_parse(mock_ics_source)

        # Assert
        assert result == expected_events  # Operation succeeds despite storage error
        mock_ics_storage.save_to_cache.assert_called_once()

    def test_no_storage_configured(self, mock_ics_parser: Mock) -> None:
        # Arrange
        service = IcsService(ics_parser=mock_ics_parser, ics_storage=None)
        mock_ics_source = Mock(spec=UrlIcsSource)
        ics_content = "BEGIN:VCALENDAR..."
        expected_events = [Mock(spec=Event)]
        mock_ics_source.get_ics_string.return_value = ics_content
        mock_ics_parser.try_parse.return_value = expected_events

        # Act
        result = service.try_fetch_and_parse(mock_ics_source)

        # Assert
        assert result == expected_events


class TestValidateIcsUrl:
    def test_successful_validation(
        self,
        service: IcsService,
        mock_ics_source: Mock,
        mock_events: list[Event],
    ) -> None:
        # Arrange
        service.try_fetch_and_parse = Mock(return_value=mock_events)  # type: ignore

        # Act
        result = service.validate_ics_url(mock_ics_source)

        # Assert
        assert isinstance(result, ValidateIcsUrlOutput)
        assert result.valid is True
        assert result.error is None
        assert result.nbEvents == len(mock_events)
        service.try_fetch_and_parse.assert_called_once_with(
            mock_ics_source, save_to_storage=True
        )

    def test_source_error(
        self,
        service: IcsService,
        mock_ics_source: Mock,
    ) -> None:
        # Arrange
        error = IcsSourceError("Failed to fetch calendar")
        service.try_fetch_and_parse = Mock(return_value=error)  # type: ignore

        # Act
        result = service.validate_ics_url(mock_ics_source)

        # Assert
        assert isinstance(result, ValidateIcsUrlOutput)
        assert result.valid is False
        assert result.error == str(error)
        assert result.nbEvents is None

    def test_parsing_error(
        self,
        service: IcsService,
        mock_ics_source: Mock,
    ) -> None:
        # Arrange
        error = IcsParsingError("Invalid calendar format")
        service.try_fetch_and_parse = Mock(return_value=error)  # type: ignore

        # Act
        result = service.validate_ics_url(mock_ics_source)

        # Assert
        assert isinstance(result, ValidateIcsUrlOutput)
        assert result.valid is False
        assert result.error == str(error)
        assert result.nbEvents is None

    def test_storage_parameter_passed(
        self,
        service: IcsService,
        mock_ics_source: Mock,
        mock_events: list[Event],
    ) -> None:
        # Arrange
        service.try_fetch_and_parse = Mock(return_value=mock_events)  # type: ignore

        # Act
        service.validate_ics_url(mock_ics_source, save_to_storage=False)

        # Assert
        service.try_fetch_and_parse.assert_called_once_with(
            mock_ics_source, save_to_storage=False
        )
