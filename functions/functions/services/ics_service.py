import logging
from dataclasses import dataclass
from typing import Any

from functions.infrastructure.event_bus import IEventBus, LocalEventBus
from functions.models.schemas import ValidateIcsUrlOutput
from functions.services.exceptions.ics import (
    BaseIcsError,
    IcsParsingError,
    IcsSourceError,
)
from functions.shared import domain_events
from functions.shared.event import Event
from functions.synchronizer.ics_cache import IcsFileStorage
from functions.synchronizer.ics_parser import IcsParser
from functions.synchronizer.ics_source import IcsSource, UrlIcsSource

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
        """
        Initializes the IcsService with an event bus and an optional ICS parser.
        
        If no ICS parser is provided, a default IcsParser instance is used.
        """
        self.ics_parser = ics_parser or IcsParser()
        self.event_bus = event_bus

    def try_fetch_and_parse(
        self,
        ics_source: IcsSource,
        metadata: dict[str, Any] | None = None,
    ) -> IcsFetchAndParseResult | IcsSourceError | IcsParsingError:
        """
        Fetches an ICS file from the given source and parses it into events.
        
        Attempts to retrieve the ICS content from the specified source, publishes an event with the fetched data and optional metadata, and parses the content into event objects. Returns either the parsed events and raw ICS string, or an error if fetching or parsing fails.
        
        Args:
            ics_source: The source from which to fetch the ICS file.
            metadata: Optional metadata to include with the published event.
        
        Returns:
            An IcsFetchAndParseResult with parsed events and raw ICS content if successful, or an error instance (IcsSourceError or IcsParsingError) if fetching or parsing fails.
        
        Raises:
            Exception: If an unexpected error occurs that is not a subclass of BaseIcsError.
        """

        try:
            ics_str = ics_source.get_ics_string()
            self.event_bus.publish(
                domain_events.IcsFetched(
                    ics_str=ics_str,
                    metadata=metadata,
                )
            )
        except IcsSourceError as e:
            logger.error(f"Failed to fetch ICS file from source: {e}")
            return e

        events_or_error = self.ics_parser.try_parse(ics_str)

        if isinstance(events_or_error, IcsParsingError):
            return events_or_error

        return IcsFetchAndParseResult(events=events_or_error, raw_ics=ics_str)

    def validate_ics_url(
        self,
        ics_source: UrlIcsSource,
        metadata: dict[str, Any] | None = None,
    ) -> ValidateIcsUrlOutput:
        """
        Validates an ICS URL by fetching and parsing its contents.
        
        Attempts to retrieve and parse the ICS file from the provided URL source. Returns a validation result indicating whether the ICS file is valid, an error message if validation fails, and the number of events if successful.
        
        Args:
            ics_source: The URL-based ICS source to validate.
            metadata: Optional metadata to include with the validation process.
        
        Returns:
            A ValidateIcsUrlOutput object with validation status, error message if any, and the number of parsed events.
        """
        result_or_error = self.try_fetch_and_parse(
            ics_source,
            metadata=metadata,
        )

        if isinstance(result_or_error, BaseIcsError):
            return ValidateIcsUrlOutput(
                valid=False,
                error=str(result_or_error),
                nbEvents=None,
            )

        return ValidateIcsUrlOutput(
            valid=True,
            error=None,
            nbEvents=len(result_or_error.events),
        )
