from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from google.cloud import storage
from pydantic import HttpUrl

from functions.synchronizer.ics_cache import (
    FirebaseIcsFileStorage,
    IcsFileStorage,
    format_exception,
)
from functions.synchronizer.ics_source import StringIcsSource, UrlIcsSource

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


def test_format_exception_none() -> None:
    """Test format_exception with None input."""
    result = format_exception(None)
    assert result is None


def test_format_exception_exception() -> None:
    """Test format_exception with an Exception input."""
    exception = ValueError("Test error")
    result = format_exception(exception)
    assert result == {"type": "ValueError", "message": "Test error"}


def test_format_exception_string() -> None:
    """Test format_exception with a string input."""
    result = format_exception("error message")
    assert result == "error message"


# Fixtures for FirebaseIcsFileStorage tests
@pytest.fixture
def bucket_mock() -> MagicMock:
    """Create a mock bucket for Firebase storage testing."""
    return MagicMock(spec=storage.Bucket)


@pytest.fixture
def blob_mock() -> MagicMock:
    """Create a mock blob for Firebase storage testing."""
    return MagicMock(spec=storage.Blob)


@pytest.fixture
def firebase_storage(
    bucket_mock: MagicMock, blob_mock: MagicMock
) -> FirebaseIcsFileStorage:
    """Create a FirebaseIcsFileStorage instance with mocked dependencies."""
    bucket_mock.blob.return_value = blob_mock
    return FirebaseIcsFileStorage(bucket_mock)


@patch("functions.synchronizer.ics_cache.datetime")
def test_save_to_cache_with_url_source(
    mock_datetime: MagicMock,
    firebase_storage: FirebaseIcsFileStorage,
    bucket_mock: MagicMock,
    blob_mock: MagicMock,
) -> None:
    """Test saving to cache with a UrlIcsSource"""
    # Arrange
    ics_source = UrlIcsSource(url=HttpUrl("https://example.com/calendar.ics"))
    metadata = {"sync_profile_id": "test-profile-123"}

    # Mock the datetime to return a predictable value
    mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    mock_datetime.now.return_value = mock_now

    # Act
    firebase_storage.save_to_cache(
        valid_ics_content, ics_source=ics_source, metadata=metadata
    )

    # Assert
    expected_filename = "test-profile-123_2023-01-01_12-00-00.ics"
    bucket_mock.blob.assert_called_once_with(expected_filename)
    blob_mock.upload_from_string.assert_called_once_with(
        valid_ics_content, content_type="text/calendar"
    )

    # Check that metadata was properly set
    expected_metadata = {
        "ics_source": ics_source.model_dump(),
        "blob_created_at": mock_now.isoformat(),
        "sync_profile_id": "test-profile-123",
    }
    assert blob_mock.metadata == expected_metadata


@patch("functions.synchronizer.ics_cache.datetime")
def test_save_to_cache_with_no_metadata(
    mock_datetime: MagicMock,
    firebase_storage: FirebaseIcsFileStorage,
    bucket_mock: MagicMock,
    blob_mock: MagicMock,
) -> None:
    """Test saving to cache with no metadata provided"""
    # Arrange
    ics_source = UrlIcsSource(url=HttpUrl("https://example.com/calendar.ics"))

    # Mock the datetime to return a predictable value
    mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    mock_datetime.now.return_value = mock_now

    # Act
    firebase_storage.save_to_cache(valid_ics_content, ics_source=ics_source)

    # Assert
    filename = mock_now.strftime("unknown-sync-profile_%Y-%m-%d_%H-%M-%S.ics")
    bucket_mock.blob.assert_called_once_with(filename)

    # Check that metadata was properly set with default values
    expected_metadata = {
        "ics_source": ics_source.model_dump(),
        "blob_created_at": mock_now.isoformat(),
    }
    assert blob_mock.metadata == expected_metadata


def test_save_to_cache_with_exception_in_metadata(
    firebase_storage: FirebaseIcsFileStorage, blob_mock: MagicMock
) -> None:
    """Test saving to cache with an exception in metadata"""
    # Arrange
    ics_source = StringIcsSource(ics_string=valid_ics_content)
    test_exception = ValueError("Test error")
    metadata = {"sync_profile_id": "test-profile-456", "error": test_exception}

    # Act
    firebase_storage.save_to_cache(
        valid_ics_content, ics_source=ics_source, metadata=metadata
    )

    # Assert
    blob_mock.upload_from_string.assert_called_once_with(
        valid_ics_content, content_type="text/calendar"
    )

    # Check that the exception was properly formatted in metadata
    assert "error" in blob_mock.metadata
    assert blob_mock.metadata["error"] == {
        "type": "ValueError",
        "message": "Test error",
    }


def test_list_files(
    firebase_storage: FirebaseIcsFileStorage, bucket_mock: MagicMock
) -> None:
    """Test listing files in the storage"""
    # Arrange
    mock_blob1 = MagicMock()
    mock_blob1.name = "test1.ics"
    mock_blob1.updated = datetime(2023, 1, 1)
    mock_blob1.metadata = {"key": "value1"}
    mock_blob1.size = 1000

    mock_blob2 = MagicMock()
    mock_blob2.name = "test2.ics"
    mock_blob2.updated = datetime(2023, 1, 2)
    mock_blob2.metadata = {"key": "value2"}
    mock_blob2.size = 2000

    bucket_mock.list_blobs.return_value = [mock_blob1, mock_blob2]

    # Act
    result = firebase_storage.list_files(prefix="test")

    # Assert
    bucket_mock.list_blobs.assert_called_once_with(prefix="test")
    assert len(result) == 2
    assert result[0]["name"] == "test1.ics"
    assert result[1]["name"] == "test2.ics"


def test_get_file_content(
    firebase_storage: FirebaseIcsFileStorage,
    bucket_mock: MagicMock,
    blob_mock: MagicMock,
) -> None:
    """Test retrieving file content"""
    # Arrange
    blob_mock.download_as_text.return_value = valid_ics_content

    # Act
    result = firebase_storage.get_file_content("test.ics")

    # Assert
    bucket_mock.blob.assert_called_once_with("test.ics")
    blob_mock.download_as_text.assert_called_once()
    assert result == valid_ics_content


def test_get_file_metadata(
    firebase_storage: FirebaseIcsFileStorage,
    bucket_mock: MagicMock,
    blob_mock: MagicMock,
) -> None:
    """Test retrieving file metadata"""
    # Arrange
    test_metadata = {"key": "value"}
    blob_mock.metadata = test_metadata

    # Act
    result = firebase_storage.get_file_metadata("test.ics")

    # Assert
    bucket_mock.blob.assert_called_once_with("test.ics")
    blob_mock.reload.assert_called_once()
    assert result == test_metadata


def test_get_file_metadata_none(
    firebase_storage: FirebaseIcsFileStorage, blob_mock: MagicMock
) -> None:
    """Test retrieving file metadata when none exists"""
    # Arrange
    blob_mock.metadata = None

    # Act
    result = firebase_storage.get_file_metadata("test.ics")

    # Assert
    assert result == {}
