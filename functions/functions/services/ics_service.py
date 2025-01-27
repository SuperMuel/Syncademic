import logging

from functions.models.schemas import ValidateIcsUrlOutput
from functions.services.exceptions.ics import (
    BaseIcsError,
    IcsParsingError,
    IcsSourceError,
)
from functions.shared.event import Event
from functions.synchronizer.ics_cache import IcsFileStorage
from functions.synchronizer.ics_parser import IcsParser
from functions.synchronizer.ics_source import IcsSource, UrlIcsSource

logger = logging.getLogger(__name__)


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
        events = service.try_fetch_and_parse(
            ics_source=UrlIcsSource(url="https://example.com/calendar.ics")
        )
        if not isinstance(events, BaseIcsError):
            for event in events:
                print(f"Event: {event.title}")
        ```
    """

    def __init__(
        self,
        ics_parser: IcsParser | None = None,
        ics_storage: IcsFileStorage | None = None,
    ) -> None:
        self.ics_parser = ics_parser or IcsParser()
        self.ics_storage = ics_storage

    def _try_save_to_storage(
        self,
        *,
        ics_source: IcsSource,
        ics_str: str,
        save_to_storage: bool,
        metadata: dict | None = None,
    ) -> None:
        if not save_to_storage or not self.ics_storage:
            logger.info("Not saving to storage")
            return

        try:
            self.ics_storage.save_to_cache(
                ics_source=ics_source,
                ics_str=ics_str,
                metadata=metadata,
            )

        except Exception as e:
            logger.error(f"Failed to save ICS file to storage: {e}")

    def try_fetch_and_parse(
        self,
        ics_source: IcsSource,
        *,
        save_to_storage: bool = True,
        metadata: dict | None = None,
    ) -> list[Event] | IcsSourceError | IcsParsingError:
        """
        Tries to fetch the ICS file and parse it. Optionally saves the ICS file to storage for debugging purposes.

        Args:
            ics_source: The source to fetch the ICS file from
            save_to_storage: If True, the ICS file is stored in storage, whether the parsing is successful or not.
            metadata: Metadata to add to the ICS file in storage.

        Returns:
            list[Event] if successful, otherwise a BaseIcsError.

        Raises:
            Exception: When an error other than BaseIcsError occurs.
        """
        try:
            ics_str = ics_source.get_ics_string()
        except IcsSourceError as e:
            logger.error(f"Failed to fetch ICS file from source: {e}")
            return e

        events_or_error = self.ics_parser.try_parse(ics_str)

        self._try_save_to_storage(
            ics_source=ics_source,
            ics_str=ics_str,
            save_to_storage=save_to_storage,
            metadata=metadata,
        )

        return events_or_error

    def validate_ics_url(
        self,
        ics_source: UrlIcsSource,
        *,
        save_to_storage: bool = True,
    ) -> ValidateIcsUrlOutput:
        """
        Validates an ICS URL by attempting to fetch and parse its contents.

        Args:
            ics_source: The source to fetch the ICS file from
            save_to_storage: If True, the ICS file is stored in storage.

        Returns:
            ValidateIcsUrlOutput: Contains validation results including:
                - valid: Whether the ICS file is valid
                - error: Error message if validation failed
                - nbEvents: Number of events if validation succeeded
        """
        events_or_error = self.try_fetch_and_parse(
            ics_source,
            save_to_storage=save_to_storage,
        )

        return ValidateIcsUrlOutput(
            valid=not isinstance(events_or_error, BaseIcsError),
            error=str(events_or_error)
            if isinstance(events_or_error, BaseIcsError)
            else None,
            nbEvents=len(events_or_error)
            if not isinstance(events_or_error, BaseIcsError)
            else None,
        )
