from datetime import datetime
import pytest
from mockfirestore import MockFirestore

from backend.models.authorization import BackendAuthorization
from backend.repositories.backend_authorization_repository import (
    FirestoreBackendAuthorizationRepository,
)


@pytest.fixture
def mock_db():
    """Provides a fresh MockFirestore instance per test, then resets it."""
    db = MockFirestore()
    yield db
    db.reset()


def test_get_authorization_not_found(mock_db):
    repo = FirestoreBackendAuthorizationRepository(db=mock_db)
    user_id = "user123"
    provider_account_id = "google_user_789"

    # There's no doc in the mock DB for user123google_user_789 yet
    result = repo.get_authorization(user_id, provider_account_id)
    assert result is None


def test_get_authorization_found(mock_db):
    repo = FirestoreBackendAuthorizationRepository(db=mock_db)
    user_id = "user123"
    provider_account_id = "google_user_789"

    # We'll manually create the doc in the mock DB
    doc_id = user_id + provider_account_id
    mock_db.collection("backendAuthorizations").document(doc_id).set(
        BackendAuthorization(
            userId=user_id,
            provider="google",
            providerAccountId=provider_account_id,
            providerAccountEmail="test@example.com",
            accessToken="abc123",
            refreshToken="def456",
            expirationDate=datetime.now(),
        ).model_dump()
    )

    result = repo.get_authorization(user_id, provider_account_id)
    assert result is not None
    assert result.userId == user_id
    assert result.providerAccountId == provider_account_id
    assert result.accessToken == "abc123"


def test_set_authorization(mock_db):
    repo = FirestoreBackendAuthorizationRepository(db=mock_db)

    auth = BackendAuthorization(
        userId="user123",
        provider="google",
        providerAccountId="google_user_789",
        providerAccountEmail="test@example.com",
        accessToken="abc123",
        refreshToken="def456",
    )

    repo.set_authorization(auth)

    # Check the doc in the mock DB
    doc_id = "user123google_user_789"
    doc = mock_db.collection("backendAuthorizations").document(doc_id).get()
    assert doc.exists

    data = doc.to_dict()
    assert data["accessToken"] == "abc123"
    assert data["refreshToken"] == "def456"


def test_set_authorizatio_already_exists(mock_db):
    repo = FirestoreBackendAuthorizationRepository(db=mock_db)

    auth = BackendAuthorization(
        userId="user123",
        provider="google",
        providerAccountId="google_user_789",
        providerAccountEmail="test@example.com",
        accessToken="abc123",
        refreshToken="def456",
    )

    repo.set_authorization(auth)

    auth = auth.model_copy(update={"accessToken": "new_token"})

    repo.set_authorization(auth)

    # Check the doc in the mock DB
    doc_id = "user123google_user_789"
    doc = mock_db.collection("backendAuthorizations").document(doc_id).get()
    assert doc.exists

    data = doc.to_dict()
    assert data["accessToken"] == "new_token"
    assert data["refreshToken"] == "def456"


def test_delete_authorization(mock_db):
    repo = FirestoreBackendAuthorizationRepository(db=mock_db)
    user_id = "user123"
    provider_account_id = "google_user_789"

    doc_id = user_id + provider_account_id
    mock_db.collection("backendAuthorizations").document(doc_id).set({"any": "data"})

    repo.delete_authorization(user_id, provider_account_id)
    doc = mock_db.collection("backendAuthorizations").document(doc_id).get()
    assert not doc.exists, "Document should be deleted"


def test_exists_false(mock_db):
    repo = FirestoreBackendAuthorizationRepository(db=mock_db)
    user_id = "user123"
    provider_account_id = "google_user_789"

    # No doc in the mock DB
    assert repo.exists(user_id, provider_account_id) is False


def test_exists_true(mock_db):
    repo = FirestoreBackendAuthorizationRepository(db=mock_db)
    user_id = "user123"
    provider_account_id = "google_user_789"

    doc_id = user_id + provider_account_id
    mock_db.collection("backendAuthorizations").document(doc_id).set({"foo": "bar"})

    assert repo.exists(user_id, provider_account_id) is True
