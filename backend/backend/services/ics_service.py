import logging
from dataclasses import dataclass
from typing import Any

from backend.infrastructure.event_bus import IEventBus, LocalEventBus
from backend.models.schemas import ValidateIcsUrlOutput
from backend.services.exceptions.ics import (
    BaseIcsError,
    IcsParsingError,
    IcsSourceError,
)
from backend.shared import domain_events
from backend.shared.event import Event
from backend.synchronizer.ics_cache import IcsFileStorage
from backend.synchronizer.ics_parser import IcsParser
from backend.synchronizer.ics_source import IcsSource, UrlIcsSource

logger = logging.getLogger(__name__)


@dataclass
class IcsFetchAndParseResult:
    events: list[Event]
    raw_ics: str


class IcsService:
    """
    Service for handling ICS (iCalendar) file operations including fetching, parsing, and validation.

    This service coordinates the interaction between different ICS-related components:
    - Fetching calendar data from URLs via UrlIcsSource
    - Parsing ICS content into Event objects via IcsParser
    - Optional storage of raw ICS files for debugging via IcsFileStorage

    The service provides error handling and a consistent interface for ICS operations,
    ensuring that failures in fetching or parsing are handled gracefully and optionally
    logged for debugging.

    Attributes:
        ics_parser (IcsParser): Component responsible for parsing ICS strings into Events
        ics_storage (IcsFileStorage | None): Optional storage for raw ICS files

    Example:
        ```python
        service = IcsService(ics_storage=IcsFileStorage())

        # Validate a calendar URL
        result = service.validate_ics_url(
            ics_source=UrlIcsSource(url="https://example.com/calendar.ics")
        )
        if result.valid:
            print(f"Found {result.nbEvents} valid events")
        else:
            print(f"Invalid calendar: {result.error}")

        # Fetch and parse events
        result = service.try_fetch_and_parse(
            ics_source=UrlIcsSource(url="https://example.com/calendar.ics")
        )
        if not isinstance(result, BaseIcsError):
            for event in result.events:
                print(f"Event: {event.title}")
            print(f"Raw ICS content: {result.raw_ics[:100]}...")
        ```
    """

    def __init__(
        self,
        event_bus: IEventBus,
        ics_parser: IcsParser | None = None,
    ) -> None:
        self.ics_parser = ics_parser or IcsParser()
        self.event_bus = event_bus

    def _enrich_metadata(
        self, metadata: dict[str, Any] | None, ics_source: IcsSource
    ) -> dict[str, Any]:
        if metadata is None:
            metadata = {}

        if isinstance(ics_source, UrlIcsSource) and "url" not in metadata:
            metadata["url"] = str(ics_source.url)

        return metadata

    def try_fetch_and_parse(
        self,
        ics_source: IcsSource,
        metadata: dict[str, Any] | None = None,
    ) -> IcsFetchAndParseResult | IcsSourceError | IcsParsingError:
        """
        Tries to fetch the ICS file and parse it.

        Args:
            ics_source: The source to fetch the ICS file from
            metadata: Additional metadata to pass to the event bus (e.g. sync_profile_id, user_id,...)
        Returns:
            IcsFetchAndParseResult (with events and raw_ics) if successful, otherwise a BaseIcsError.

        Raises:
            Exception: When an error other than BaseIcsError occurs.
        """

        metadata = self._enrich_metadata(metadata, ics_source)

        try:
            ics_str = ics_source.get_ics_string()
            self.event_bus.publish(
                domain_events.IcsFetched(
                    ics_str=ics_str,
                    metadata=metadata,
                )
            )
        except IcsSourceError as e:
            logger.error("Failed to fetch ICS file from source: %s", e)
            return e

        events_or_error = self.ics_parser.try_parse(ics_str)

        if isinstance(events_or_error, IcsParsingError):
            return events_or_error

        return IcsFetchAndParseResult(events=events_or_error, raw_ics=ics_str)

    def validate_ics_url_or_raise(
        self,
        ics_source: IcsSource,
        metadata: dict[str, Any] | None = None,
    ) -> IcsFetchAndParseResult:
        """
        Validates an ICS URL by attempting to fetch and parse its contents.

        Args:
            ics_source: The source to fetch the ICS file from
            metadata: Additional metadata to pass to the event bus (e.g. sync_profile_id, user_id,...)

        Returns:
            IcsFetchAndParseResult if successful

        Raises:
            BaseIcsError: If the ICS URL is invalid.
        """
        result_or_error = self.try_fetch_and_parse(
            ics_source,
            metadata=metadata,
        )

        if isinstance(result_or_error, BaseIcsError):
            raise result_or_error

        return result_or_error

    def validate_ics_url(
        self,
        ics_source: IcsSource,
        metadata: dict[str, Any] | None = None,
    ) -> ValidateIcsUrlOutput:
        try:
            result = self.validate_ics_url_or_raise(ics_source, metadata)
        except BaseIcsError as e:
            return ValidateIcsUrlOutput(
                valid=False,
                error=str(e),
                nb_events=None,
            )

        return ValidateIcsUrlOutput(
            valid=True,
            error=None,
            nb_events=len(result.events),
        )
