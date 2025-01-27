import io
from abc import ABC, abstractmethod
from pathlib import Path

import requests
import validators
from firebase_functions import logger
from pydantic import BaseModel, HttpUrl

from functions.settings import settings


class IcsSource(BaseModel, ABC):
    @abstractmethod
    def get_ics_string(self) -> str:
        pass


class UrlIcsSource(IcsSource):
    url: HttpUrl

    def __init__(self, url: str | HttpUrl, **data):
        if isinstance(url, str) and not validators.url(url):
            raise ValueError("Invalid URL")
        super().__init__(url=url, **data)

    def get_ics_string(
        self,
        *,
        timeout_s: int = settings.URL_ICS_SOURCE_TIMEOUT_S,
        max_content_size_b: int = settings.MAX_ICS_SIZE_BYTES,
    ) -> str:
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
                    raise ValueError(f"Content-Type is not text : {content_type}")

                # Check the Content-Length header if available
                content_length = response.headers.get("Content-Length")
                if content_length is not None:
                    content_length = int(content_length)
                    if content_length > max_content_size_b:
                        logger.info(
                            f"Content-Length is too large ({content_length/1_048_576:.2f}MB > {max_content_size_b/1_048_576:.2f}MB) ({response.headers=})"
                        )
                        raise ValueError("ICS file is too large.")

                # Use BytesIO to accumulate chunks
                chunks = io.BytesIO()
                total_bytes = 0

                # Collect raw bytes first
                for chunk in response.iter_content(chunk_size=8192):
                    total_bytes += len(chunk)
                    if total_bytes > max_content_size_b:
                        raise ValueError("ICS file is too large.")
                    chunks.write(chunk)

                # Decode all bytes at once
                return chunks.getvalue().decode("utf-8", errors="ignore")

        except requests.RequestException as e:
            logger.error(f"Could not fetch ICS file : {e}")
            raise ValueError(f"Could not fetch ICS file : {e}")


class FileIcsSource(IcsSource):
    file_path: Path

    def get_ics_string(self) -> str:
        with open(self.file_path, "r") as file:
            return file.read()


class StringIcsSource(IcsSource):
    ics_string: str

    def get_ics_string(self) -> str:
        return self.ics_string
