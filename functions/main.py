from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

import logging
from typing import Any
from firebase_functions import https_fn, scheduler_fn

from firebase_functions.firestore_fn import (
    on_document_created,
    on_document_deleted,
    on_document_updated,
    on_document_written,
    Event,
    DocumentSnapshot,
)

from firebase_admin import initialize_app, firestore
from firebase_functions.params import StringParam

from firebase_functions import firestore_fn, https_fn, logger


from synchronizer.synchronizer.synchronizer import perform_synchronization
from synchronizer.synchronizer.middleware.insa_middleware import (
    TitlePrettifier,
    ExamPrettifier,
)

#   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   TODO: Add one more level of synchronizer


initialize_app()


CLIENT_ID = StringParam("CLIENT_ID")
CLIENT_SECRET = StringParam("CLIENT_SECRET")


def get_calendar_service(access_token):
    # Construct a Credentials object from the access token
    credentials = Credentials(
        client_id=CLIENT_ID.value,
        # client_secret="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",
        token=access_token,
    )

    # Build the Google Calendar API service
    service = build("calendar", "v3", credentials=credentials)

    return service


@on_document_created(document="users/{userId}/syncProfiles/{syncProfileId}")  # type: ignore
def on_sync_profile_created(event: Event[DocumentSnapshot]):
    logging.info(f"Sync profile created: {event.data}")

    doc = event.data.to_dict()

    if doc is None:
        # ? Why would this happen?
        raise ValueError("Document has been created but is None")

    target_calendar = doc["targetCalendar"]
    scheduleSource = doc["scheduleSource"]

    target_calendar_id = target_calendar["id"]
    source_url = scheduleSource["url"]
    sync_profile_id = event.params["syncProfileId"]
    userId = event.params["userId"]

    access_token = target_calendar["accessToken"]
    service = get_calendar_service(access_token)

    db = firestore.client()
    sync_profile_ref = (
        db.collection("users")
        .document(userId)
        .collection("syncProfiles")
        .document(sync_profile_id)
    )

    status = doc.get("status")

    # is synchronization in progress, do nothing
    if status == "in_progress":
        logger.info("Synchronization is in progress, skipping")
        return

    # mark that synchronization is in progress
    sync_profile_ref.update({"status": "in_progress"})

    try:
        perform_synchronization(
            syncConfigId=sync_profile_id,
            icsSourceUrl=source_url,
            targetCalendarId=target_calendar_id,
            service=service,
            middlewares=[TitlePrettifier, ExamPrettifier],
        )
        sync_profile_ref.update({"status": "success"})
        logger.info("Synchronization completed successfully")
    except Exception as e:
        sync_profile_ref.update({"status": "error", "error": str(e)})
        logger.info(f"Synchronization failed: {e}")
        raise e
