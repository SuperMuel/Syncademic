# tests/test_sync_stats_repository.py

import pytest
from datetime import date
from unittest.mock import patch

from mockfirestore import MockFirestore

from functions.repositories.sync_stats_repository import FirestoreSyncStatsRepository


@pytest.fixture
def mock_db():
    """Provides a fresh MockFirestore instance per test, then resets it."""
    db = MockFirestore()
    yield db
    db.reset()


def test_get_daily_sync_count_not_found(mock_db):
    """If no document exists for the given date, return 0."""
    repo = FirestoreSyncStatsRepository(db=mock_db)
    user_id = "user123"
    day = date(2025, 1, 1)

    count = repo.get_daily_sync_count(user_id, day)
    assert count == 0


def test_get_daily_sync_count_found(mock_db):
    """If the document has a syncCount, return it."""
    repo = FirestoreSyncStatsRepository(db=mock_db)
    user_id = "user123"
    day = date(2025, 1, 1)

    # Create the document in mock Firestore
    doc_id = day.isoformat()  # '2025-01-01'
    (
        mock_db.collection("users")
        .document(user_id)
        .collection("syncStats")
        .document(doc_id)
        .set({"syncCount": 5})
    )

    count = repo.get_daily_sync_count(user_id, day)
    assert count == 5


# # This test is disabled for now because mock-firestore library
# # doesn't support the Increment operation on inexistent documents.
#
# def test_increment_sync_count_new_document(mock_db):
#     """If the document doesn't exist yet, we create it with syncCount=1."""
#     repo = FirestoreSyncStatsRepository(db=mock_db)
#     user_id = "user123"
#     day = date(2025, 1, 1)

#     repo.increment_sync_count(user_id, day)

#     # Now verify the document was created with syncCount=1
#     doc_id = day.isoformat()
#     doc = (
#         mock_db.collection("users")
#         .document(user_id)
#         .collection("syncStats")
#         .document(doc_id)
#         .get()
#     )
#     assert doc.exists
#     assert doc.to_dict()["syncCount"] == 1


def test_increment_sync_count_existing_document(mock_db):
    """If the document exists, increment should add 1 to the existing count."""
    repo = FirestoreSyncStatsRepository(db=mock_db)
    user_id = "user123"
    day = date(2025, 1, 1)

    doc_id = day.isoformat()
    (
        mock_db.collection("users")
        .document(user_id)
        .collection("syncStats")
        .document(doc_id)
        .set({"syncCount": 5})
    )

    repo.increment_sync_count(user_id, day)

    doc = (
        mock_db.collection("users")
        .document(user_id)
        .collection("syncStats")
        .document(doc_id)
        .get()
    )
    assert doc.to_dict()["syncCount"] == 6


def test_get_daily_sync_count_with_none_date(mock_db):
    """Test that get_daily_sync_count uses today's date when day=None."""
    repo = FirestoreSyncStatsRepository(db=mock_db)
    user_id = "user123"
    today = date(2025, 1, 1)

    with patch("functions.repositories.sync_stats_repository.date") as mock_date:
        mock_date.today.return_value = today

        # Set up data for today
        doc_id = today.isoformat()
        (
            mock_db.collection("users")
            .document(user_id)
            .collection("syncStats")
            .document(doc_id)
            .set({"syncCount": 3})
        )

        count = repo.get_daily_sync_count(user_id, day=None)
        assert count == 3
        mock_date.today.assert_called_once()


def test_increment_sync_count_with_none_date(mock_db):
    """Test that increment_sync_count uses today's date when day=None."""
    repo = FirestoreSyncStatsRepository(db=mock_db)
    user_id = "user123"
    today = date(2025, 1, 1)

    with patch("functions.repositories.sync_stats_repository.date") as mock_date:
        mock_date.today.return_value = today

        # First set up initial data
        doc_id = today.isoformat()
        (
            mock_db.collection("users")
            .document(user_id)
            .collection("syncStats")
            .document(doc_id)
            .set({"syncCount": 5})
        )

        repo.increment_sync_count(user_id, day=None)

        # Verify the increment happened for today's document
        doc = (
            mock_db.collection("users")
            .document(user_id)
            .collection("syncStats")
            .document(doc_id)
            .get()
        )
        assert doc.to_dict()["syncCount"] == 6
        mock_date.today.assert_called_once()
