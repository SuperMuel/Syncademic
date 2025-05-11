from pathlib import Path

import pytest
import requests
import responses
from pydantic import HttpUrl, ValidationError

from backend.services.exceptions.ics import IcsSourceError
from backend.settings import settings
from backend.synchronizer.ics_source import (
    FileIcsSource,
    StringIcsSource,
    UrlIcsSource,
)

# Mock settings
settings.MAX_ICS_SIZE_BYTES = 1 * 1024 * 1024  # 1 MB

# Sample ICS content
valid_ics_content = """
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Your Organization//Your Product//EN
BEGIN:VEVENT
UID:123456
DTSTAMP:20240101T120000Z
DTSTART:20240101T130000Z
DTEND:20240101T140000Z
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR
"""

large_ics_content = "A" * (settings.MAX_ICS_SIZE_BYTES + 1)  # Just over 1 MB

invalid_content_type = "This is not ICS content"

invalid_url = "htp:/invalid-url"


def test_valid_ics_url_with_content_length():
    url = HttpUrl("https://example.com/valid.ics")

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            str(url),
            body=valid_ics_content,
            status=200,
            content_type="text/calendar",
            adding_headers={"Content-Length": str(len(valid_ics_content))},
        )

        ics_source = UrlIcsSource(url=url)
        ics_string = ics_source.get_ics_string()
        assert ics_string == valid_ics_content


def test_valid_ics_url_without_content_length():
    url = HttpUrl("https://example.com/valid.ics")

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            str(url),
            body=valid_ics_content,
            status=200,
            content_type="text/calendar",
            # No Content-Length header
        )

        ics_source = UrlIcsSource(url=url)
        ics_string = ics_source.get_ics_string()
        assert ics_string == valid_ics_content


def test_ics_file_too_large_with_content_length():
    url = HttpUrl("https://example.com/large.ics")

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            str(url),
            body=large_ics_content,
            status=200,
            content_type="text/calendar",
            adding_headers={"Content-Length": str(len(large_ics_content))},
        )

        ics_source = UrlIcsSource(url=url)
        with pytest.raises(IcsSourceError, match="ICS file is too large"):
            ics_source.get_ics_string()


def test_ics_file_too_large_without_content_length():
    url = HttpUrl("https://example.com/large.ics")

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            str(url),
            body=large_ics_content,
            status=200,
            content_type="text/calendar",
            # No Content-Length header
        )

        ics_source = UrlIcsSource(url=url)
        with pytest.raises(IcsSourceError, match="ICS file is too large"):
            ics_source.get_ics_string()


def test_http_error():
    url = HttpUrl("https://example.com/notfound.ics")

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            str(url),
            body="Not Found",
            status=404,
            content_type="text/plain",
        )

        ics_source = UrlIcsSource(url=url)
        with pytest.raises(IcsSourceError, match="Could not fetch ICS file"):
            ics_source.get_ics_string()


def test_invalid_content_type():
    url = HttpUrl("https://example.com/invalid-content-type.ics")

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            str(url),
            body=valid_ics_content,
            status=200,
            content_type="application/pdf",
            adding_headers={"Content-Length": str(len(valid_ics_content))},
        )

        ics_source = UrlIcsSource(url=url)
        with pytest.raises(IcsSourceError, match="Content-Type is not text"):
            ics_source.get_ics_string()


def test_missing_content_type():
    url = HttpUrl("https://example.com/valid.ics")

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            str(url),
            body=valid_ics_content,
            status=200,
            adding_headers={"Content-Length": str(len(valid_ics_content))},
        )

        ics_source = UrlIcsSource(url=url)
        ics_string = ics_source.get_ics_string()
        assert ics_string == valid_ics_content


@pytest.mark.parametrize(
    "content_type",
    ["text/calendar", "text/plain"],
)
def test_valid_content_type(content_type):
    url = HttpUrl("https://example.com/valid.ics")

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            str(url),
            body=valid_ics_content,
            status=200,
            content_type=content_type,
            adding_headers={"Content-Length": str(len(valid_ics_content))},
        )

        ics_source = UrlIcsSource(url=url)
        ics_string = ics_source.get_ics_string()
        assert ics_string == valid_ics_content


def test_invalid_url():
    url = invalid_url

    with pytest.raises(ValidationError):
        UrlIcsSource(url=url)  # type: ignore


def test_timeout():
    url = HttpUrl("https://example.com/timeout.ics")

    with responses.RequestsMock() as rsps:

        def request_callback(request):
            raise requests.exceptions.Timeout()

        rsps.add_callback(
            responses.GET,
            str(url),
            callback=request_callback,
            content_type="text/calendar",
        )

        ics_source = UrlIcsSource(url=url)
        with pytest.raises(IcsSourceError, match="Could not fetch ICS file"):
            ics_source.get_ics_string()


def test_url_ics_source_equality():
    url = HttpUrl("https://example.com/calendar.ics")
    source1 = UrlIcsSource(url=url)
    source2 = UrlIcsSource(url=url)
    source3 = UrlIcsSource(url=HttpUrl("https://example.com/different.ics"))

    assert source1 == source2
    assert source1 != source3
    assert source1 != "not an ics source"


def test_file_ics_source_equality():
    path1 = Path("/tmp/calendar1.ics")
    path2 = Path("/tmp/calendar2.ics")
    source1 = FileIcsSource(file_path=path1)
    source2 = FileIcsSource(file_path=path1)
    source3 = FileIcsSource(file_path=path2)

    assert source1 == source2
    assert source1 != source3
    assert source1 != "not an ics source"


def test_string_ics_source_equality():
    content = "BEGIN:VCALENDAR\nEND:VCALENDAR"
    source1 = StringIcsSource(ics_string=content)
    source2 = StringIcsSource(ics_string=content)
    source3 = StringIcsSource(ics_string="different content")

    assert source1 == source2
    assert source1 != source3
    assert source1 != "not an ics source"


def test_different_source_types_inequality():
    url_source = UrlIcsSource(url=HttpUrl("https://example.com/calendar.ics"))
    file_source = FileIcsSource(file_path=Path("/tmp/calendar.ics"))
    string_source = StringIcsSource(ics_string="BEGIN:VCALENDAR\nEND:VCALENDAR")

    assert url_source != file_source
    assert url_source != string_source
    assert file_source != string_source


def test_webcal_to_http_url_conversion():
    webcal_url = "webcal://example.com/calendar.ics?version=2.0&type=personal"
    converted = UrlIcsSource.from_str(webcal_url)
    assert (
        str(converted.url)
        == "http://example.com/calendar.ics?version=2.0&type=personal"
    )
