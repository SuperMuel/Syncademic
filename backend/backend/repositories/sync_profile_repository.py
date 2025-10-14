import logging
from typing import Protocol

from firebase_admin.firestore import firestore
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1.document import DocumentReference

from backend.models.sync_profile import (
    SyncProfile,
    SyncProfileStatusType,
)

logger = logging.getLogger(__name__)


class ISyncProfileRepository(Protocol):
    """
    Repository handling all CRUD operations for SyncProfile documents
    under:  users/{userId}/syncProfiles/{syncProfileId}
    """

    def get_sync_profile(
        self, user_id: str, sync_profile_id: str
    ) -> SyncProfile | None:
        """
        Retrieves a SyncProfile by user_id and sync_profile_id.
        Returns None if not found.
        """
        ...

    def list_user_sync_profiles(self, user_id: str) -> list[SyncProfile]:
        """
        Lists all SyncProfiles for a given user.
        """
        ...

    def list_all_sync_profiles(self) -> list[SyncProfile]:
        """
        Lists all SyncProfiles for all users.
        """
        ...

    def list_all_active_sync_profiles(self) -> list[SyncProfile]:
        """
        Lists all active SyncProfiles for all users.
        """
        ...

    def save_sync_profile(self, profile: SyncProfile) -> None:
        """
        Saves (creates or updates) a SyncProfile by overwriting.
        """
        ...

    def delete_sync_profile(self, user_id: str, sync_profile_id: str) -> None:
        """
        Deletes a SyncProfile document.
        """

        ...


class FirestoreSyncProfileRepository(ISyncProfileRepository):
    """
    Concrete Firestore implementation of ISyncProfileRepository.
    Manages syncProfiles subcollection under each user document.
    """

    def __init__(self, db: firestore.Client | None = None):
        """
        :param db: Optionally inject a Firestore client (useful for testing).
        """
        self._db = db or firestore.Client()

    def _get_doc_ref(self, user_id: str, sync_profile_id: str) -> DocumentReference:
        """Helper to get the document reference."""
        return (
            self._db.collection("users")
            .document(user_id)
            .collection("syncProfiles")
            .document(sync_profile_id)
        )

    def get_sync_profile(
        self, user_id: str, sync_profile_id: str
    ) -> SyncProfile | None:
        """
        Retrieves a SyncProfile by user_id and sync_profile_id.
        Returns None if not found.
        """
        logger.info(
            "Getting sync profile %s for user %s",
            sync_profile_id,
            user_id,
        )

        doc_ref: DocumentReference = self._get_doc_ref(user_id, sync_profile_id)

        data = doc_ref.get().to_dict()

        if not data:
            return None

        data["id"] = sync_profile_id
        data["user_id"] = user_id

        return SyncProfile.model_validate(data)

    def save_sync_profile(self, profile: SyncProfile) -> None:
        """Saves (creates or updates) a SyncProfile by overwriting."""
        logger.info(
            "Saving SyncProfile %s for user %s",
            profile.id,
            profile.user_id,
        )
        doc_ref = self._get_doc_ref(profile.user_id, profile.id)

        data_to_save = profile.model_dump()

        doc_ref.set(data_to_save)
        logger.info("Saved SyncProfile %s", profile.id)

    def list_user_sync_profiles(self, user_id: str) -> list[SyncProfile]:
        """
        Lists all SyncProfiles for a given user.
        """
        logger.info("Listing sync profiles for user %s", user_id)

        collection_ref: CollectionReference = (
            self._db.collection("users").document(user_id).collection("syncProfiles")
        )

        query = collection_ref.stream()

        profiles: list[SyncProfile] = []

        for doc in query:
            doc: DocumentSnapshot
            if data := doc.to_dict():
                data["id"] = doc.id
                data["user_id"] = user_id
                profiles.append(SyncProfile.model_validate(data))

        return profiles

    def list_all_sync_profiles(self) -> list[SyncProfile]:
        """
        Lists all SyncProfiles for all users.
        Uses Firestore collectionGroup on 'syncProfiles'.
        """
        query = self._db.collection_group("syncProfiles").stream()

        profiles: list[SyncProfile] = []

        for doc in query:
            doc: DocumentSnapshot
            if data := doc.to_dict():
                data["id"] = doc.id
                data["user_id"] = doc.reference.parent.parent.id
                profiles.append(SyncProfile.model_validate(data))

        return profiles

    def list_all_active_sync_profiles(self) -> list[SyncProfile]:
        """
        Lists all active SyncProfiles for all users.

        A profile is considered active if it can be synchronized
        (i.e., not currently being processed or deleted).

        """
        logger.info("Listing active sync profiles")

        query = self._db.collection_group("syncProfiles").where(
            "status.type",
            "in",
            [status.value for status in SyncProfileStatusType if status.is_active()],
        )

        profiles: list[SyncProfile] = []

        for doc in query.stream():
            doc: DocumentSnapshot

            if data := doc.to_dict():
                data["id"] = doc.id
                data["user_id"] = doc.reference.parent.parent.id
                profiles.append(SyncProfile.model_validate(data))

        return profiles

    def delete_sync_profile(self, user_id: str, sync_profile_id: str) -> None:
        """
        Deletes a SyncProfile document.

        Warning: This method only deletes the document from Firestore. Unlike SyncProfileService.delete(),
        it does not clean up associated data like calendar events. Use with caution.
        """
        logger.info(
            "Deleting sync profile %s for user %s",
            sync_profile_id,
            user_id,
        )

        doc_ref: DocumentReference = self._get_doc_ref(user_id, sync_profile_id)
        doc_ref.delete()


class MockSyncProfileRepository(ISyncProfileRepository):
    """
    An in-memory implementation of ISyncProfileRepository for testing.

    Stores SyncProfiles in a nested dictionary keyed by (user_id, sync_profile_id).
    All operations (CRUD, listing) are performed against this in-memory storage
    without interacting with Firestore.
    """

    def __init__(self) -> None:
        # Structure: { user_id: { sync_profile_id: SyncProfile } }
        self._storage: dict[str, dict[str, SyncProfile]] = {}

    def get_sync_profile(
        self, user_id: str, sync_profile_id: str
    ) -> SyncProfile | None:
        user_profiles = self._storage.get(user_id, {})
        return user_profiles.get(sync_profile_id, None)

    def save_sync_profile(self, profile: SyncProfile) -> None:
        user_profiles = self._storage.setdefault(profile.user_id, {})
        user_profiles[profile.id] = profile

    def list_user_sync_profiles(self, user_id: str) -> list[SyncProfile]:
        # Return all SyncProfiles for a single user, or an empty list if not found.
        user_profiles = self._storage.get(user_id, {})
        return list(user_profiles.values())

    def list_all_sync_profiles(self) -> list[SyncProfile]:
        # Flatten all user profiles into one list.
        all_profiles = []
        for user_profiles in self._storage.values():
            all_profiles.extend(user_profiles.values())
        return all_profiles

    def list_all_active_sync_profiles(self) -> list[SyncProfile]:
        # A profile is active if sync_profile.status.type.is_active() is True
        # (meaning status is NOT in [IN_PROGRESS, DELETING, DELETION_FAILED]).
        active_profiles = []
        for user_profiles in self._storage.values():
            for profile in user_profiles.values():
                if profile.status.type.is_active():
                    active_profiles.append(profile)
        return active_profiles

    def delete_sync_profile(self, user_id: str, sync_profile_id: str) -> None:
        if user_id in self._storage and sync_profile_id in self._storage[user_id]:
            del self._storage[user_id][sync_profile_id]
