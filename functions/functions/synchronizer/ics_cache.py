from abc import ABC, abstractmethod
from datetime import datetime, timezone
from functions.synchronizer.ics_source import UrlIcsSource
from google.cloud import storage
from firebase_functions import logger


class IcsFileStorage(ABC):
    @abstractmethod
    def save_to_cache(
        self,
        sync_profile_id: str,
        sync_trigger: str,
        ics_source: UrlIcsSource,
        ics_str: str,
        parsing_error: str | None = None,
    ) -> None:
        pass


class FirebaseIcsFileStorage(IcsFileStorage):
    def __init__(self, bucket: storage.Bucket) -> None:
        self.firebase_storage_bucket = bucket

    def save_to_cache(
        self,
        sync_profile_id: str,
        sync_trigger: str,  # TODO : type this
        ics_source: UrlIcsSource,
        ics_str: str,
        parsing_error: str | None = None,
    ) -> None:
        now = datetime.now(timezone.utc)

        filename = f"{sync_profile_id}_{now.strftime('%Y-%m-%d_%H-%M-%S')}.ics"
        blob = self.firebase_storage_bucket.blob(filename)

        blob.metadata = {
            "sourceUrl": ics_source.url,
            "syncProfileId": sync_profile_id,
            "syncTrigger": sync_trigger,
            "blob_created_at": now.isoformat(),
            "parsing_error": parsing_error,
        }
        blob.upload_from_string(ics_str, content_type="text/calendar")
        logger.info(f"Stored ics string in firebase storage: {filename}")
