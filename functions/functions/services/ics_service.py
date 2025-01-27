import logging

from functions.functions.services.exceptions.ics import (
    BaseIcsError,
    IcsParsingError,
    IcsSourceError,
)
from functions.models.schemas import ValidateIcsUrlOutput
from functions.synchronizer.ics_cache import IcsFileStorage
from functions.synchronizer.ics_parser import IcsParser
from functions.synchronizer.ics_source import UrlIcsSource
from functions.shared.event import Event

logger = logging.getLogger(__name__)


class IcsService:
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
        ics_source: UrlIcsSource,
        ics_str: str,
        save_to_storage: bool,
        parsing_error: str | Exception | None = None,
    ) -> None:
        if not save_to_storage or not self.ics_storage:
            logger.info("Not saving to storage")
            return

        try:
            self.ics_storage.save_to_cache(
                ics_source=ics_source,
                ics_str=ics_str,
                parsing_error=parsing_error,
            )

        except Exception as e:
            logger.error(f"Failed to save ICS file to storage: {e}")

    def try_fetch_and_parse(
        self,
        ics_source: UrlIcsSource,
        *,
        save_to_storage: bool = True,
    ) -> list[Event] | BaseIcsError:
        """
        Tries to fetch the ICS file and parse it. Optionally saves the ICS file to storage for debugging purposes.

        Args:
            ics_source: The source to fetch the ICS file from
            save_to_storage: If True, the ICS file is stored in storage, whether the parsing is successful or not.

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
            parsing_error=events_or_error
            if isinstance(events_or_error, Exception)
            else None,
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
            ics_source=ics_source,
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
