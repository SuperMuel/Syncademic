from datetime import datetime, timezone
from typing import Dict, Protocol

from firebase_admin.firestore import firestore
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1.document import DocumentReference
from pydantic import ValidationError

from functions.models.rules import Ruleset
from functions.models.sync_profile import (
    SyncProfile,
    SyncProfileStatus,
    SyncProfileStatusType,
)


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

    def update_sync_profile_status(
        self,
        *,
        user_id: str,
        sync_profile_id: str,
        status: SyncProfileStatus,
    ) -> None:
        """
        Replaces the status field of the SyncProfile document with the provided status.
        """

    def delete_sync_profile(self, user_id: str, sync_profile_id: str) -> None:
        """
        Deletes a SyncProfile document.
        """

        ...

    def update_created_at(self, user_id: str, sync_profile_id: str) -> None:
        """
        Updates the created_at field with the server timestamp.
        """
        ...

    def update_last_successful_sync(self, user_id: str, sync_profile_id: str) -> None:
        """
        Updates the lastSuccessfulSync field with the server timestamp.
        """
        ...

    def update_ruleset_error(
        self, user_id: str, sync_profile_id: str, error_str: str
    ) -> None:
        """Updates the ruleset_error field with the provided error message."""
        ...

    def update_ruleset(
        self, user_id: str, sync_profile_id: str, ruleset: Ruleset
    ) -> None:
        """
        Updates the ruleset field of a sync profile.
        """
        ...

    # def create_sync_profile(self, user_id: str, sync_profile: SyncProfile) -> str:
    #     """
    #     Creates a new SyncProfile document and returns the generated syncProfileId.
    #     """

    #     ...

    # def update_sync_profile(
    #     self, user_id: str, sync_profile_id: str, sync_profile: SyncProfile
    # ) -> None:
    #     """
    #     Replaces or merges the existing SyncProfile with new data.
    #     """

    #     ...

    # def patch_sync_profile(
    #     self, user_id: str, sync_profile_id: str, partial_data: dict
    # ) -> None:
    #     """
    #     Partially updates the SyncProfile document with the provided partial_data.
    #     For example, updating the status or ruleset field.
    #     """

    #     ...


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

    def get_sync_profile(
        self, user_id: str, sync_profile_id: str
    ) -> SyncProfile | None:
        """
        Retrieves a SyncProfile by user_id and sync_profile_id.
        Returns None if not found.
        """
        doc_ref: DocumentReference = (
            self._db.collection("users")
            .document(user_id)
            .collection("syncProfiles")
            .document(sync_profile_id)
        )

        data = doc_ref.get().to_dict()

        if not data:
            return None

        data["id"] = sync_profile_id
        data["user_id"] = user_id

        return SyncProfile.model_validate(data)

    def list_user_sync_profiles(self, user_id: str) -> list[SyncProfile]:
        """
        Lists all SyncProfiles for a given user.
        """
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

    def try_list_all_sync_profiles(self) -> list[SyncProfile | dict]:
        """
        Lists all SyncProfiles for all users, returning raw dicts for invalid profiles.
        Uses Firestore collectionGroup on 'syncProfiles'.

        Returns a list containing either validated SyncProfile objects or raw dicts
        for profiles that failed validation.
        """
        query = self._db.collection_group("syncProfiles").stream()
        profiles: list[SyncProfile | dict] = []

        for doc in query:
            doc: DocumentSnapshot
            if data := doc.to_dict():
                data["id"] = doc.id
                data["user_id"] = doc.reference.parent.parent.id
                try:
                    profiles.append(SyncProfile.model_validate(data))
                except ValidationError:
                    # If validation fails, append the raw dict
                    profiles.append(data)

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
        # Note :  SyncProfiles can't be disabled yet.

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

    def update_sync_profile_status(
        self,
        *,
        user_id: str,
        sync_profile_id: str,
        status: SyncProfileStatus,
    ) -> None:
        """
        Replaces the status field of the SyncProfile document with the provided status.
        """
        doc_ref: DocumentReference = (
            self._db.collection("users")
            .document(user_id)
            .collection("syncProfiles")
            .document(sync_profile_id)
        )

        doc_ref.update({"status": status.model_dump()})

    def delete_sync_profile(self, user_id: str, sync_profile_id: str) -> None:
        """
        Deletes a SyncProfile document.
        """
        doc_ref: DocumentReference = (
            self._db.collection("users")
            .document(user_id)
            .collection("syncProfiles")
            .document(sync_profile_id)
        )

        doc_ref.delete()

    def update_created_at(self, user_id: str, sync_profile_id: str) -> None:
        doc_ref: DocumentReference = (
            self._db.collection("users")
            .document(user_id)
            .collection("syncProfiles")
            .document(sync_profile_id)
        )
        doc_ref.update({"created_at": firestore.SERVER_TIMESTAMP})

    def update_last_successful_sync(self, user_id: str, sync_profile_id: str) -> None:
        doc_ref: DocumentReference = (
            self._db.collection("users")
            .document(user_id)
            .collection("syncProfiles")
            .document(sync_profile_id)
        )
        doc_ref.update({"lastSuccessfulSync": firestore.SERVER_TIMESTAMP})

    def update_ruleset_error(
        self, user_id: str, sync_profile_id: str, error_str: str
    ) -> None:
        """Updates the ruleset_error field with the provided error message."""
        doc_ref: DocumentReference = (
            self._db.collection("users")
            .document(user_id)
            .collection("syncProfiles")
            .document(sync_profile_id)
        )
        doc_ref.update({"ruleset_error": error_str})

    def update_ruleset(
        self, user_id: str, sync_profile_id: str, ruleset: Ruleset
    ) -> None:
        """
        Updates the ruleset field of a sync profile.
        """
        doc_ref: DocumentReference = (
            self._db.collection("users")
            .document(user_id)
            .collection("syncProfiles")
            .document(sync_profile_id)
        )

        # We store the ruleset as a JSON string in Firestore.
        doc_ref.update({"ruleset": ruleset.model_dump_json()})


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

    def update_sync_profile_status(
        self,
        *,
        user_id: str,
        sync_profile_id: str,
        status: SyncProfileStatus,
    ) -> None:
        # Update the status of an existing profile. No-op if not found.
        if user_id not in self._storage:
            return
        if sync_profile_id not in self._storage[user_id]:
            return

        existing_profile = self._storage[user_id][sync_profile_id]
        # Replace existing status
        updated_profile = existing_profile.model_copy(update={"status": status})
        self._storage[user_id][sync_profile_id] = updated_profile

    def delete_sync_profile(self, user_id: str, sync_profile_id: str) -> None:
        if user_id in self._storage and sync_profile_id in self._storage[user_id]:
            del self._storage[user_id][sync_profile_id]

    def update_created_at(self, user_id: str, sync_profile_id: str) -> None:
        # No-op if profile doesn't exist.
        if user_id not in self._storage:
            return
        if sync_profile_id not in self._storage[user_id]:
            return

        existing_profile = self._storage[user_id][sync_profile_id]
        updated_profile = existing_profile.model_copy(
            update={
                "created_at": datetime.now(timezone.utc),
            }
        )
        self._storage[user_id][sync_profile_id] = updated_profile

    def update_last_successful_sync(self, user_id: str, sync_profile_id: str) -> None:
        # Same as above, but for lastSuccessfulSync.
        if user_id not in self._storage:
            return
        if sync_profile_id not in self._storage[user_id]:
            return

        existing_profile = self._storage[user_id][sync_profile_id]
        updated_profile = existing_profile.model_copy(
            update={
                "lastSuccessfulSync": datetime.now(timezone.utc),
            }
        )
        self._storage[user_id][sync_profile_id] = updated_profile

    def update_ruleset_error(
        self, user_id: str, sync_profile_id: str, error_str: str
    ) -> None:
        # Set the ruleset_error field
        if user_id not in self._storage:
            return
        if sync_profile_id not in self._storage[user_id]:
            return

        existing_profile = self._storage[user_id][sync_profile_id]
        updated_profile = existing_profile.model_copy(
            update={
                "ruleset_error": error_str,
            }
        )
        self._storage[user_id][sync_profile_id] = updated_profile

    def update_ruleset(
        self, user_id: str, sync_profile_id: str, ruleset: Ruleset
    ) -> None:
        # Update the ruleset field in memory.
        if user_id not in self._storage:
            return
        if sync_profile_id not in self._storage[user_id]:
            return

        existing_profile = self._storage[user_id][sync_profile_id]
        updated_profile = existing_profile.model_copy(
            update={
                "ruleset": ruleset,
                "ruleset_error": None,  # clear any previous error
            }
        )
        self._storage[user_id][sync_profile_id] = updated_profile

    # Optional: a helper to create or store a profile (like "create_sync_profile")
    # to facilitate tests that require a pre-existing profile in the repository.
    def store_sync_profile(self, profile: SyncProfile) -> None:
        """
        A convenience method (not in the Protocol) to manually store or overwrite
        a SyncProfile in memory. Useful for tests that need a pre-existing profile.
        """
        user_profiles = self._storage.setdefault(profile.user_id, {})
        user_profiles[profile.id] = profile
