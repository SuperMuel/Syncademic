from datetime import date
from typing import Protocol

from google.cloud import firestore
from google.cloud.firestore_v1.document import DocumentReference


class ISyncStatsRepository(Protocol):
    """
    Repository for tracking daily synchronization statistics for each user.

    Sync stats measure how many synchronizations a user has performed on a given day.
    This information can be used to implement usage limits, provide insights,
    or bill users based on their synchronization activity.

    The typical Firestore path for these stats is:
        users/{userId}/syncStats/{YYYY-MM-DD}
    """

    def get_daily_sync_count(self, user_id: str, day: date | None = None) -> int:
        """
        Retrieves the syncCount for the given user on a specific date (UTC).
        Returns 0 if not found.
        """
        ...

    def increment_sync_count(self, user_id: str, day: date | None = None) -> None:
        """
        Increments the syncCount by 1 for the given user on the specified date.
        Creates the document if it doesn't exist.
        """
        ...


class FirestoreSyncStatsRepository(ISyncStatsRepository):
    """
    Concrete implementation of ISyncStatsRepository using Google Firestore.
    """

    def __init__(self, db: firestore.Client | None = None):
        """
        :param db: Optionally inject a Firestore client (useful for testing).
                   If not provided, a default client is created.
        """
        self._db = db or firestore.Client()

    def get_daily_sync_count(self, user_id: str, day: date | None = None) -> int:
        """
        Retrieves the syncCount for the given user on a specific date (UTC).
        Returns 0 if not found.

        :param user_id: The user ID.
        :param day: The date for which to retrieve the sync count. If None, defaults to today.
        """
        if day is None:
            day = date.today()

        doc_id = day.isoformat()  # e.g. "2024-01-20"
        doc_ref: DocumentReference = (
            self._db.collection("users")
            .document(user_id)
            .collection("syncStats")
            .document(doc_id)
        )

        data = doc_ref.get().to_dict()

        if data is None:
            return 0

        return data.get("syncCount", 0)

    def increment_sync_count(self, user_id: str, day: date | None = None) -> None:
        """
        Increments the syncCount by 1 for the given user on the specified date.
        Creates the document if it doesn't exist.

        :param user_id: The user ID.
        :param day: The date for which to retrieve the sync count. If None, defaults to today.
        """
        if day is None:
            day = date.today()

        doc_id = day.isoformat()
        doc_ref: DocumentReference = (
            self._db.collection("users")
            .document(user_id)
            .collection("syncStats")
            .document(doc_id)
        )

        doc_ref.set({"syncCount": firestore.Increment(1)}, merge=True)
