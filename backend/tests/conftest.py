import os

import pytest


# Tests import `Settings()`, which requires `FIREBASE_STORAGE_BUCKET` at
# instantiation time. Provide a deterministic default so collection never
# triggers validation errors before fixtures run.
TEST_FIREBASE_STORAGE_BUCKET = "test-firebase-storage-bucket"
CLIENT_SECRET = "test-client-secret"
OPENAI_API_KEY = "test-openai-api-key"

os.environ.setdefault("FIREBASE_STORAGE_BUCKET", TEST_FIREBASE_STORAGE_BUCKET)
os.environ.setdefault("CLIENT_SECRET", CLIENT_SECRET)
os.environ.setdefault("OPENAI_API_KEY", OPENAI_API_KEY)


@pytest.fixture(autouse=True)
def _set_firebase_storage_bucket(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FIREBASE_STORAGE_BUCKET", TEST_FIREBASE_STORAGE_BUCKET)
    monkeypatch.setenv("CLIENT_SECRET", CLIENT_SECRET)
    monkeypatch.setenv("OPENAI_API_KEY", OPENAI_API_KEY)
