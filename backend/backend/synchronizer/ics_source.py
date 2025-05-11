import io
from abc import ABC, abstractmethod
from pathlib import Path

import requests
from firebase_functions import logger
from pydantic import BaseModel, HttpUrl

from backend.settings import settings
from backend.services.exceptions.ics import IcsSourceError


class IcsSource(BaseModel, ABC):
    """
    Base class for ICS sources.
    """

    @abstractmethod
    def get_ics_string(self) -> str:
        """
        Retrieves the ICS calendar data as a string.

        Returns:
            str: The ICS calendar data as a string.

        Raises:
            IcsSourceError: If there is an error retrieving the ICS data.
        """
        pass


class UrlIcsSource(IcsSource):
    """
    ICS calendar source that fetches calendar data from a URL.

    This class handles the safe retrieval of ICS data from remote URLs,
    implementing various safety checks including:
    - Content-Type validation to ensure text-based responses
    - Content size limits to prevent memory issues
    - Timeout controls for network requests
    - Proper UTF-8 decoding of the response

    Attributes:
        url (HttpUrl): The URL from which to fetch the ICS calendar data.
            Validated using Pydantic's HttpUrl type.

    Example:
        ```python
        # Create from string URL, automatically converting webcal to http
        source = UrlIcsSource.from_str("webcal://example.com/calendar.ics")

        # Or create directly with an HttpUrl
        from pydantic import HttpUrl
        source = UrlIcsSource(url=HttpUrl("https://example.com/calendar.ics"))

        try:
            ics_data = source.get_ics_string()
        except IcsSourceError as e:
            print(f"Failed to fetch calendar: {e}")
        ```
    """

    url: HttpUrl

    @classmethod
    def from_str(cls, url_str: str) -> "UrlIcsSource":
        """
        Create a UrlIcsSource from a string URL, converting webcal:// to http:// if needed.

        Args:
            url_str: The URL string, which may use webcal:// or http(s)://

        Returns:
            UrlIcsSource: A new instance with the processed URL
        """
        if url_str.startswith("webcal://"):
            url_str = "http://" + url_str[9:]
        return cls(url=HttpUrl(url_str))

    def get_ics_string(
        self,
        *,
        timeout_s: int = settings.URL_ICS_SOURCE_TIMEOUT_S,
        max_content_size_b: int = settings.MAX_ICS_SIZE_BYTES,
    ) -> str:
        """
        Safely fetch and return ICS calendar data from a URL.

        Args:
            timeout_s: Request timeout in seconds.
            max_content_size_b: Maximum allowed size of ICS file in bytes. Preventing
                large files from being fetched and processed.

        Returns:
            str: The ICS calendar data as a string.

        Raises:
            IcsSourceError: If there is an error fetching or processing the ICS file,
                including timeout, size limits, or invalid content type.
        """
        logger.info(f"Fetching ICS file from {self.url}")
        try:
            with requests.get(
                str(self.url), stream=True, timeout=timeout_s
            ) as response:
                response.raise_for_status()

                # Check the Content-Type header
                content_type = response.headers.get("Content-Type")
                if content_type is not None and "text" not in content_type:
                    logger.info(f"Content-Type is not text : {content_type}")
                    raise IcsSourceError(f"Content-Type is not text : {content_type}")

                # Check the Content-Length header if available
                content_length = response.headers.get("Content-Length")
                if content_length is not None:
                    content_length = int(content_length)
                    if content_length > max_content_size_b:
                        logger.info(
                            f"Content-Length is too large ({content_length / 1_048_576:.2f}MB > {max_content_size_b / 1_048_576:.2f}MB) ({response.headers=})"
                        )
                        raise IcsSourceError("ICS file is too large.")

                # Use BytesIO to accumulate chunks
                chunks = io.BytesIO()
                total_bytes = 0

                # Collect raw bytes first
                for chunk in response.iter_content(chunk_size=8192):
                    total_bytes += len(chunk)
                    if total_bytes > max_content_size_b:
                        raise IcsSourceError("ICS file is too large.")
                    chunks.write(chunk)

                # Decode all bytes at once
                s = chunks.getvalue().decode("utf-8", errors="ignore")
                logger.info(f"ICS string size: {len(s) / 1024} KB")
                return s

        except requests.RequestException as e:
            logger.error(f"Could not fetch ICS file : {e}")
            raise IcsSourceError(f"Could not fetch ICS file. ", original_exception=e)


class FileIcsSource(IcsSource):
    """
    ICS source that is a file path, for testing purposes.
    """

    file_path: Path

    def get_ics_string(self) -> str:
        """
        Reads and returns ICS calendar data from a file.

        Returns:
            str: The ICS calendar data as a string.

        Raises:
            IcsSourceError: If there is an error reading the file.
        """
        try:
            with open(self.file_path, "r") as file:
                return file.read()
        except Exception as e:
            raise IcsSourceError(f"Could not read ICS file: {e}", original_exception=e)


class StringIcsSource(IcsSource):
    """
    ICS source that is already a string, for testing purposes.
    """

    ics_string: str

    def get_ics_string(self) -> str:
        """
        Returns the stored ICS calendar string.

        Returns:
            str: The ICS calendar data as a string.
        """
        return self.ics_string
