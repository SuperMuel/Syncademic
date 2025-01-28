from typing import Protocol
from google.cloud import firestore
from functions.models.authorization import BackendAuthorization


class IBackendAuthorizationRepository(Protocol):
    """
    Repository that manages backend authorizations (OAuth credentials),
    stored in the 'backendAuthorizations' collection.
    """

    def get_authorization(
        self, user_id: str, provider_account_id: str
    ) -> BackendAuthorization | None:
        """
        Returns the BackendAuthorization document if it exists, otherwise None.
        """

        ...

    def set_authorization(self, backend_auth: BackendAuthorization) -> None:
        """
        Creates or replaces the backend authorization document in Firestore.
        """

        ...

    def delete_authorization(self, user_id: str, provider_account_id: str) -> None:
        """
        Deletes the backend authorization document from Firestore.
        """

        ...

    def exists(self, user_id: str, provider_account_id: str) -> bool:
        """
        Returns True if there is a valid BackendAuthorization document for the given user
        and provider_account_id, otherwise False. It doesn't acutally check if the token is expired or
        if the user has revoked the access. It only checks if the document exists.
        """

        ...


class FirestoreBackendAuthorizationRepository(IBackendAuthorizationRepository):
    """
    Concrete Firestore implementation of IBackendAuthorizationRepository.
    Manages documents in the 'backendAuthorizations' top-level collection.
    """

    def __init__(self, db: firestore.Client | None = None):
        """
        :param db: Optionally inject a Firestore client for testing or advanced usage.
        """
        self._db = db or firestore.Client()

    def get_authorization(
        self, user_id: str, provider_account_id: str
    ) -> BackendAuthorization | None:
        """
        Returns the BackendAuthorization document if it exists, otherwise None.
        """
        doc_id = user_id + provider_account_id
        doc_ref = self._db.collection("backendAuthorizations").document(doc_id)

        data = doc_ref.get().to_dict()

        if not data:
            return None

        return BackendAuthorization.model_validate(data)

    def set_authorization(self, backend_auth: BackendAuthorization) -> None:
        """
        Creates or replaces the backend authorization document in Firestore.
        """
        doc_id = backend_auth.userId + backend_auth.providerAccountId
        doc_ref = self._db.collection("backendAuthorizations").document(doc_id)

        doc_ref.set(backend_auth.model_dump())

    def delete_authorization(self, user_id: str, provider_account_id: str) -> None:
        """
        Deletes the backend authorization document from Firestore.
        """
        doc_id = user_id + provider_account_id
        doc_ref = self._db.collection("backendAuthorizations").document(doc_id)
        doc_ref.delete()

    def exists(self, user_id: str, provider_account_id: str) -> bool:
        """
        Returns True if a backend authorization document exists for (user_id + provider_account_id), else False.
        (This does not validate token freshness or revocation.)
        """
        doc_id = user_id + provider_account_id
        doc_ref = self._db.collection("backendAuthorizations").document(doc_id)
        return doc_ref.get().exists
