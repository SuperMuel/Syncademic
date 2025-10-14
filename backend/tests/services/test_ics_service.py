from unittest.mock import Mock

import arrow
import pytest
from pydantic import HttpUrl, parse_obj_as

from backend.infrastructure.event_bus import MockEventBus
from backend.models.schemas import ValidateIcsUrlOutput
from backend.services.exceptions.ics import IcsParsingError, IcsSourceError
from backend.services.ics_service import IcsService, IcsFetchAndParseResult
from backend.shared import domain_events
from backend.shared.event import Event
from backend.synchronizer.ics_parser import IcsParser
from backend.synchronizer.ics_source import IcsSource, UrlIcsSource


@pytest.fixture
def mock_events() -> list[Event]:
    now = arrow.now()
    return [
        Event(start=now, end=now.shift(hours=1), title="Event 1"),
        Event(start=now.shift(days=1), end=now.shift(days=1, hours=2), title="Event 2"),
    ]


@pytest.fixture
def mock_ics_source() -> Mock:
    return Mock(spec=IcsSource)


@pytest.fixture
def mock_ics_parser() -> Mock:
    return Mock(spec=IcsParser)


@pytest.fixture
def mock_ics_storage() -> Mock:
    return Mock()


@pytest.fixture
def mock_url_ics_source() -> Mock:
    return Mock(spec=IcsSource)


@pytest.fixture
def mock_event_bus() -> MockEventBus:
    return MockEventBus()


@pytest.fixture
def service(
    mock_ics_parser: Mock, mock_ics_storage: Mock, mock_event_bus: MockEventBus
) -> IcsService:
    return IcsService(
        ics_parser=mock_ics_parser,
        event_bus=mock_event_bus,
    )


class TestTryFetchAndParse:
    def test_successful_fetch_and_parse(
        self,
        service: IcsService,
        mock_ics_source: Mock,
        mock_ics_parser: Mock,
        mock_event_bus: MockEventBus,
    ) -> None:
        # Arrange
        ics_content = "BEGIN:VCALENDAR..."
        expected_events = [Mock(spec=Event), Mock(spec=Event)]
        mock_ics_source.get_ics_string.return_value = ics_content
        mock_ics_parser.try_parse.return_value = expected_events

        # Act
        result = service.try_fetch_and_parse(mock_ics_source, metadata={"test": "test"})

        # Assert
        assert isinstance(result, IcsFetchAndParseResult)
        assert result.events == expected_events
        assert result.raw_ics == ics_content
        mock_ics_source.get_ics_string.assert_called_once()
        mock_ics_parser.try_parse.assert_called_once_with(ics_content)
        mock_event_bus.assert_event_published_with_data(
            domain_events.IcsFetched,
            ics_str=ics_content,
            metadata={"test": "test"},
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
        mock_event_bus: MockEventBus,
    ) -> None:
        # Arrange
        ics_content = "BEGIN:VCALENDAR..."
        error = IcsParsingError("Invalid format")
        mock_ics_source.get_ics_string.return_value = ics_content
        mock_ics_parser.try_parse.return_value = error

        # Act
        result = service.try_fetch_and_parse(mock_ics_source, metadata={"test": "test"})

        # Assert
        assert result == error
        mock_ics_source.get_ics_string.assert_called_once()
        mock_ics_parser.try_parse.assert_called_once_with(ics_content)
        mock_event_bus.assert_event_published_with_data(
            domain_events.IcsFetched,
            ics_str=ics_content,
            metadata={"test": "test"},
        )


class TestValidateIcsUrl:
    def test_successful_validation(
        self,
        service: IcsService,
        mock_ics_source: Mock,
        mock_events: list[Event],
    ) -> None:
        # Arrange
        service.try_fetch_and_parse = Mock(  # type: ignore
            return_value=IcsFetchAndParseResult(
                events=mock_events,
                raw_ics="mock irrelevant ics value",
            )
        )

        # Act
        result = service.validate_ics_url(mock_ics_source, metadata={"test": "test"})

        # Assert
        assert isinstance(result, ValidateIcsUrlOutput)
        assert result.valid is True
        assert result.error is None
        assert result.nb_events == len(mock_events)
        service.try_fetch_and_parse.assert_called_once_with(
            mock_ics_source, metadata={"test": "test"}
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
        assert result.nb_events is None

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
        assert result.nb_events is None


def test_enrich_metadata_adds_url_when_missing():
    from backend.services.ics_service import IcsService
    from backend.synchronizer.ics_source import UrlIcsSource, IcsSource
    from unittest.mock import Mock
    from pydantic import HttpUrl

    event_bus = Mock()
    event_bus.publish = Mock()
    service = IcsService(event_bus=event_bus)
    ics_source = UrlIcsSource(url=HttpUrl("https://example.com/test.ics"))

    # Case 1: metadata is None
    result = service._enrich_metadata(None, ics_source)
    assert result["url"] == "https://example.com/test.ics"

    # Case 2: metadata is present but no url
    result = service._enrich_metadata({"foo": "bar"}, ics_source)
    assert result["url"] == "https://example.com/test.ics"
    assert result["foo"] == "bar"

    # Case 3: metadata already has url
    result = service._enrich_metadata({"url": "should-not-change"}, ics_source)
    assert result["url"] == "should-not-change"

    # Case 4: ics_source is not UrlIcsSource
    class DummySource(IcsSource):
        def get_ics_string(self):
            return ""

    dummy_source = DummySource()
    result = service._enrich_metadata({"foo": "bar"}, dummy_source)
    assert result == {"foo": "bar"}
