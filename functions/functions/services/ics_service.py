import logging

from pydantic import HttpUrl

from functions.functions.models.schemas import ValidateIcsUrlOutput
from functions.functions.synchronizer.ics_cache import IcsFileStorage
from functions.functions.synchronizer.ics_parser import IcsParser
from functions.functions.synchronizer.ics_source import UrlIcsSource
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
        ics_source_url: str,
        ics_str: str,
        save_to_storage: bool,
        parsing_error: str | Exception | None = None,
    ) -> None:
        if not save_to_storage or not self.ics_storage:
            logger.info("Not saving to storage")
            return

        try:
            self.ics_storage.save_to_cache(
                ics_source_url=ics_source_url,
                ics_str=ics_str,
                parsing_error=parsing_error,
            )

        except Exception as e:
            logger.error(f"Failed to save ICS file to storage: {e}")

    def _try_parse_ics(self, ics_str: str) -> list[Event] | Exception:
        """
        Parses the ICS file and returns the events or an exception.
        """
        try:
            return self.ics_parser.parse(ics_str=ics_str)
        except Exception as e:
            logger.error(f"Failed to parse ICS file: {e}")
            return e

    def validate_ics_url(
        self,
        ics_url: str | HttpUrl,
        *,
        save_to_storage: bool = True,
    ) -> ValidateIcsUrlOutput:
        """
        1) Fetches the ICS file from the URL (streaming + size checks).
        2) Parses the ICS file to detect if it is valid.

        Returns:
            ValidateIcsUrlOutput: The result of the validation.

        If save_to_storage is True, the ICS file is stored in Firebase Storage, and
        we store some metadata along with it.
        """

        try:
            ics_source = UrlIcsSource(ics_url)
            ics_str = ics_source.get_ics_string()
        except Exception as e:
            logger.error(f"Failed to fetch ICS file from URL: {e}")
            return ValidateIcsUrlOutput(
                valid=False,
                error=str(e),
            )

        events_or_error = self._try_parse_ics(ics_str=ics_str)

        self._try_save_to_storage(
            ics_source_url=str(ics_url),
            ics_str=ics_str,
            save_to_storage=save_to_storage,
            parsing_error=events_or_error
            if isinstance(events_or_error, Exception)
            else None,
        )

        return ValidateIcsUrlOutput(
            valid=not isinstance(events_or_error, Exception),
            error=str(events_or_error)
            if isinstance(events_or_error, Exception)
            else None,
            nbEvents=len(events_or_error)
            if not isinstance(events_or_error, Exception)
            else None,
        )
