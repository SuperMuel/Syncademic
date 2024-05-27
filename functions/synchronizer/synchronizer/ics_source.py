from abc import ABC, abstractmethod
import validators
from pathlib import Path
import requests


class IcsSource(ABC):
    @abstractmethod
    def get_ics_string(self) -> str:
        pass


class UrlIcsSource(IcsSource):
    def __init__(self, url: str):
        if not validators.url(url):
            raise ValueError("Invalid URL")
        self.url = url

    def get_ics_string(self) -> str:
        # TODO : check content_type
        try:
            response = requests.get(self.url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ValueError(f"Could not fetch ics file from internet: {e}")

        # For testing purpose, we want to download ics files from github, which is not a calendar file.
        # So we don't check the content type for now.
        # if "text/calendar" not in response.headers["Content-Type"]:
        #     raise ValueError(f"Content type is {response.headers['Content-Type']}")

        return response.text


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
