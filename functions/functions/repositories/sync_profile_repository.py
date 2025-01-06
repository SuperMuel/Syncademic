from typing import Protocol
from firebase_admin.firestore import firestore
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.firestore_v1.collection import CollectionReference


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

        return SyncProfile(id=sync_profile_id, user_id=user_id, **data)

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
                profiles.append(SyncProfile(id=doc.id, user_id=user_id, **data))

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
                profiles.append(
                    SyncProfile(
                        id=doc.id, user_id=doc.reference.parent.parent.id, **data
                    )
                )

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
                profiles.append(
                    SyncProfile(
                        id=doc.id, user_id=doc.reference.parent.parent.id, **data
                    )
                )

        return profiles

    def update_sync_profile_status(
        self,
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
