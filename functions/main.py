# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from os import access

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build, Resource

import logging
from typing import Any
from firebase_functions import https_fn, scheduler_fn

from firebase_functions.firestore_fn import (
    on_document_created,
    on_document_deleted,
    on_document_updated,
    on_document_written,
    Event,
    Change,
    DocumentSnapshot,
)

from firebase_admin import firestore, initialize_app
from firebase_functions.params import StringParam

from firebase_functions import firestore_fn, https_fn

import google.cloud.firestore

from ..synchronizer.synchronizer.synchronizer import perform_synchronization

#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#    TODO: Add one more level of synchronizer


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


@on_document_created(document="users/{userId}/syncProfiles/{syncProfileId}")
def on_sync_profile_created(event: Event):
    logging.info(f"Sync profile created: {event.data}")

    target_calendar = event.data["targetCalendar"]
    scheduleSource = event.data["scheduleSource"]

    target_calendar_id = target_calendar["calendarId"]
    source_url = scheduleSource["url"]
    sync_profile_id = event.params["syncProfileId"]

    access_token = target_calendar["accessToken"]
    service = get_calendar_service(access_token)

    perform_synchronization(
        syncConfigId=sync_profile_id,
        icsSourceUrl=source_url,
        targetCalendarId=target_calendar_id,
        service=service,
    )
