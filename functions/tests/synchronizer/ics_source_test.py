import pytest
import requests
import responses

from functions.settings import settings
from functions.synchronizer.ics_source import UrlIcsSource

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
    url = "https://example.com/valid.ics"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            url,
            body=valid_ics_content,
            status=200,
            content_type="text/calendar",
            adding_headers={"Content-Length": str(len(valid_ics_content))},
        )

        ics_source = UrlIcsSource(url)
        ics_string = ics_source.get_ics_string()
        assert ics_string == valid_ics_content


def test_valid_ics_url_without_content_length():
    url = "https://example.com/valid.ics"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            url,
            body=valid_ics_content,
            status=200,
            content_type="text/calendar",
            # No Content-Length header
        )

        ics_source = UrlIcsSource(url)
        ics_string = ics_source.get_ics_string()
        assert ics_string == valid_ics_content


def test_ics_file_too_large_with_content_length():
    url = "https://example.com/large.ics"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            url,
            body=large_ics_content,
            status=200,
            content_type="text/calendar",
            adding_headers={"Content-Length": str(len(large_ics_content))},
        )

        ics_source = UrlIcsSource(url)
        with pytest.raises(ValueError, match="ICS file is too large"):
            ics_source.get_ics_string()


def test_ics_file_too_large_without_content_length():
    url = "https://example.com/large.ics"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            url,
            body=large_ics_content,
            status=200,
            content_type="text/calendar",
            # No Content-Length header
        )

        ics_source = UrlIcsSource(url)
        with pytest.raises(ValueError, match="ICS file is too large"):
            ics_source.get_ics_string()


def test_http_error():
    url = "https://example.com/notfound.ics"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET, url, body="Not Found", status=404, content_type="text/plain"
        )

        ics_source = UrlIcsSource(url)
        with pytest.raises(ValueError, match="Could not fetch ICS file"):
            ics_source.get_ics_string()


def test_invalid_content_type():
    url = "https://example.com/invalid-content-type.ics"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            url,
            body=valid_ics_content,
            status=200,
            content_type="application/pdf",
            adding_headers={"Content-Length": str(len(valid_ics_content))},
        )

        ics_source = UrlIcsSource(url)
        with pytest.raises(ValueError, match="Content-Type is not text"):
            ics_source.get_ics_string()


def test_missing_content_type():
    url = "https://example.com/valid.ics"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            url,
            body=valid_ics_content,
            status=200,
            adding_headers={"Content-Length": str(len(valid_ics_content))},
        )

        ics_source = UrlIcsSource(url)
        ics_string = ics_source.get_ics_string()
        assert ics_string == valid_ics_content


@pytest.mark.parametrize(
    "content_type",
    ["text/calendar", "text/plain"],
)
def test_valid_content_type(content_type):
    url = "https://example.com/valid.ics"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            url,
            body=valid_ics_content,
            status=200,
            content_type=content_type,
            adding_headers={"Content-Length": str(len(valid_ics_content))},
        )

        ics_source = UrlIcsSource(url)
        ics_string = ics_source.get_ics_string()
        assert ics_string == valid_ics_content


def test_invalid_url():
    url = invalid_url

    with pytest.raises(ValueError, match="Invalid URL"):
        UrlIcsSource(url)


def test_timeout():
    url = "https://example.com/timeout.ics"

    with responses.RequestsMock() as rsps:

        def request_callback(request):
            raise requests.exceptions.Timeout()

        rsps.add_callback(
            responses.GET, url, callback=request_callback, content_type="text/calendar"
        )

        ics_source = UrlIcsSource(url)
        with pytest.raises(ValueError, match="Could not fetch ICS file"):
            ics_source.get_ics_string()
