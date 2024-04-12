import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow

import logging
from typing import Any
from firebase_functions import https_fn

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

from firebase_functions import https_fn, logger


from google.oauth2.credentials import Credentials

from firebase_functions import https_fn
from firebase_admin import firestore
from synchronizer.synchronizer.synchronizer import perform_synchronization

#   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   TODO: Add one more level of synchronizer

from synchronizer.synchronizer.middleware.insa_middleware import (
    TitlePrettifier,
    ExamPrettifier,
)


initialize_app()


CLIENT_ID = StringParam("CLIENT_ID")
CLIENT_SECRET = StringParam("CLIENT_SECRET")


def get_calendar_service(access_token: str, refresh_token: str | None = None):
    if not access_token or not isinstance(access_token, str):
        raise ValueError(f"{access_token=} : Not a valid access token")

    # Construct a Credentials object from the access token
    credentials = Credentials(
        client_id=CLIENT_ID.value,
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_secret=CLIENT_SECRET.value,
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

    # TODO validate the document

    _synchronize_now(
        event.params["userId"],
        event.params["syncProfileId"],
    )


@https_fn.on_call()
def request_sync(req: https_fn.CallableRequest) -> Any:
    if not req.auth:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.UNAUTHENTICATED, "Unauthorized"
        )

    syncProfileId = req.data.get("syncProfileId")

    if not syncProfileId:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INVALID_ARGUMENT, "Missing syncProfileId"
        )

    _synchronize_now(req.auth.uid, syncProfileId)


def _synchronize_now(user_id: str, sync_profile_id: str):
    db = firestore.client()

    sync_profile_ref = (
        db.collection("users")
        .document(user_id)
        .collection("syncProfiles")
        .document(sync_profile_id)
    )

    doc = sync_profile_ref.get()

    # is synchronization in progress, do nothing
    # TODO: If no status.type ??

    status = doc.get("status")
    if status and status.get("type") == "inProgress":
        logger.info("Synchronization is in progress, skipping")
        return

    # TODO: Check access token validity and refresh or send error if needed

    sync_profile_ref.update(
        {
            "status": {
                "type": "inProgress",
            }
        }
    )

    # TODO create CalendarManager here. This will allow us to test the authorization
    # and avoid doing it in the synchronization function

    try:
        perform_synchronization(
            syncProfileId=sync_profile_id,
            icsSourceUrl=doc.get("scheduleSource.url"),
            targetCalendarId=doc.get("targetCalendar.id"),
            service=get_calendar_service(
                doc.get("targetCalendar.accessToken"),
                doc.get("targetCalendar.refreshToken"),
            ),
            middlewares=[TitlePrettifier, ExamPrettifier],
        )
    except Exception as e:
        sync_profile_ref.update(
            {
                "status": {
                    "type": "failed",
                    "message": str(e),
                }
            }
        )
        logger.info(f"Synchronization failed: {e}")
        return

    sync_profile_ref.update(
        {
            "status": {
                "type": "success",
            },
            "lastSuccessfulSync": firestore.firestore.SERVER_TIMESTAMP,
        }
    )

    logger.info("Synchronization completed successfully")


@https_fn.on_call()
def authorize_backend(request: https_fn.CallableRequest) -> dict:
    if request.auth is None:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.UNAUTHENTICATED, "Unauthenticated"
        )

    auth_code = request.data.get("authCode")

    if not auth_code:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INVALID_ARGUMENT, "Missing authorization code"
        )

    user_id = request.auth.uid

    sync_profile_id = request.data.get("syncProfileId")

    if not sync_profile_id:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INVALID_ARGUMENT, "Missing sync profile ID"
        )

    db = firestore.client()

    sync_profile_ref = (
        db.collection("users")
        .document(user_id)
        .collection("syncProfiles")
        .document(sync_profile_id)
    )

    if not sync_profile_ref.get().exists:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.NOT_FOUND, "Sync profile not found"
        )

    # https://www.reddit.com/r/webdev/comments/11w1e36/warning_oauth_scope_has_changed_from/
    os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": CLIENT_ID.value,
                    "client_secret": CLIENT_SECRET.value,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=["https://www.googleapis.com/auth/calendar"],
            redirect_uri="https://syncademic-36c18.web.app",
        )

        flow.fetch_token(code=auth_code)

        credentials = flow.credentials
        access_token = credentials.token
        refresh_token = credentials.refresh_token
    except Exception as e:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL,
            f"An error occurred while exchanging the authorization code: {str(e)}",
        )

    # TODO: Move this information to a separate collection only accessible by the backend and not the user
    sync_profile_ref.update(
        {
            "targetCalendar.accessToken": access_token,
            "targetCalendar.refreshToken": refresh_token,
        }
    )

    return {"success": True}
