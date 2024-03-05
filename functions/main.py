# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.cloud import firestore
import google_auth_oauthlib.flow

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
from pyparsing import C

initialize_app()


CLIENT_ID = StringParam("CLIENT_ID")
CLIENT_SECRET = StringParam("CLIENT_SECRET")


@on_document_created(document="users/{userId}/syncProfiles/{syncProfileId}")
def on_sync_profile_created(event: Event):
    logging.info(f"Sync profile created: {event.data}")


@scheduler_fn.on_schedule(schedule="every day 03:00")
def daily_synchronization(event: scheduler_fn.ScheduledEvent):
    logging.info("Starting daily synchronization")
    # Do the synchronization here

    firestore_client: google.cloud.firestore.Client = firestore.client()

    # Get all configurations
    # firestore_client.document("another/doc").set({
    # ...
    # })

    logging.info("Daily synchronization done")


@https_fn.on_call()
def exchange_code_and_store_tokens(req: https_fn.CallableRequest) -> Any:
    if req.auth is None:
        return "Unauthorized", 401

    uid = req.auth.uid

    logging.info(f"Request: {req}")

    # Get the code from the request
    if "code" not in req.data:
        return "No code provided", 400  # TODO : Better error handling

    code = req.data["code"]

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config={
            "web": {
                "client_id": CLIENT_ID.value,
                "client_secret": CLIENT_SECRET.value,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/calendar"],
        redirect_uri="https://syncademic-36c18.firebaseapp.com/__/auth/handler",
    )

    flow.fetch_token(code=code)

    credentials = flow.credentials

    firestore_client: google.cloud.firestore.Client = firestore.client()

    doc_ref = firestore_client.collection("users").document(uid)
    doc_ref.set(
        {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
        },
        merge=True,
    )

    return "Tokens stored successfully.", 200
