from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any
from google.cloud import storage
from firebase_functions import logger

from functions.synchronizer.ics_source import IcsSource, UrlIcsSource


class IcsFileStorage(ABC):
    @abstractmethod
    def save_to_cache(
        self,
        ics_str: str,
        *,
        ics_source: IcsSource,
        metadata: dict | None = None,
    ) -> None:
        pass


def format_exception(e: Any) -> str | dict | None:
    if not e:
        return None
    if isinstance(e, Exception):
        return {
            "type": type(e).__name__,
            "message": str(e),
        }
    return str(e)


class FirebaseIcsFileStorage(IcsFileStorage):
    def __init__(self, bucket: storage.Bucket) -> None:
        self.firebase_storage_bucket = bucket

    def save_to_cache(
        self,
        ics_str: str,
        *,
        ics_source: IcsSource,
        metadata: dict | None = None,
    ) -> None:
        now = datetime.now(timezone.utc)
        if not metadata:
            metadata = {}

        # format exceptions in the metadata
        metadata = {
            k: format_exception(v)
            for k, v in metadata.items()
            if isinstance(v, Exception)
        }

        sync_profile_id = metadata.get("sync_profile_id", "unknown-sync-profile")
        filename = f"{sync_profile_id}_{now.strftime('%Y-%m-%d_%H-%M-%S')}.ics"
        blob = self.firebase_storage_bucket.blob(filename)

        blob.metadata = {
            "ics_source": ics_source.model_dump(),
            "blob_created_at": now.isoformat(),
            **metadata,
        }
        blob.upload_from_string(ics_str, content_type="text/calendar")
        logger.info(f"Stored ics string in firebase storage: {filename}")
