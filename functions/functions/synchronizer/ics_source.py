from abc import ABC, abstractmethod
import io
from functions.settings import settings
import validators
from pathlib import Path
import requests
from firebase_functions import logger


class IcsSource(ABC):
    @abstractmethod
    def get_ics_string(self) -> str:
        pass


class UrlIcsSource(IcsSource):
    def __init__(
        self,
        url: str,
        timeout_s: int = 10,
        max_content_size_b: int = settings.MAX_ICS_SIZE_BYTES,
    ):
        if not validators.url(url):
            raise ValueError("Invalid URL")
        self.url = url
        self.timeout_s = timeout_s
        self.max_content_size_b = max_content_size_b

    def get_ics_string(self) -> str:
        logger.info(f"Fetching ICS file from {self.url}")
        try:
            with requests.get(
                self.url, stream=True, timeout=self.timeout_s
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
                    if content_length > self.max_content_size_b:
                        logger.info(
                            f"Content-Length is too large ({content_length/1_048_576:.2f}MB > {self.max_content_size_b/1_048_576:.2f}MB) ({response.headers=})"
                        )
                        raise ValueError("ICS file is too large.")

                # Use BytesIO to accumulate chunks
                chunks = io.BytesIO()
                total_bytes = 0

                # Collect raw bytes first
                for chunk in response.iter_content(chunk_size=8192):
                    total_bytes += len(chunk)
                    if total_bytes > self.max_content_size_b:
                        raise ValueError("ICS file is too large.")
                    chunks.write(chunk)

                # Decode all bytes at once
                return chunks.getvalue().decode("utf-8", errors="ignore")

        except requests.RequestException as e:
            logger.error(f"Could not fetch ICS file : {e}")
            raise ValueError(f"Could not fetch ICS file : {e}")


class FileIcsSource(IcsSource):
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def get_ics_string(self) -> str:
        # read file
        with open(self.file_path, "r") as file:
            return file.read()


class StringIcsSource(IcsSource):
    def __init__(self, ics_string: str):
        self.ics_string = ics_string

    def get_ics_string(self) -> str:
        return self.ics_string
