import os
from google.oauth2.credentials import Credentials
from google.oauth2.id_token import verify_oauth2_token
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow

import logging
from typing import Any, Literal
from firebase_functions import https_fn, logger

from firebase_functions.firestore_fn import (
    on_document_created,
    on_document_deleted,
    on_document_updated,
    on_document_written,
    Event,
    DocumentSnapshot,
)
from firebase_functions import options

from firebase_admin import initialize_app, firestore
from firebase_functions.params import StringParam

from firebase_functions import https_fn, logger, scheduler_fn


from google.oauth2.credentials import Credentials

from firebase_functions import https_fn
from firebase_admin import firestore

from google.auth.transport import requests
from synchronizer.synchronizer.google_calendar_manager import (
    GoogleCalendarManager,
)
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


def get_calendar_service(user_id: str, provider_account_id: str):
    if not user_id:
        raise ValueError("User ID is required")
    if not provider_account_id:
        raise ValueError("Provider account ID is required")

    db = firestore.client()

    backend_authorization = (
        db.collection("backendAuthorizations")
        .document(user_id + provider_account_id)
        .get()
    )

    if not backend_authorization.exists:
        raise ValueError("Target calendar is not authorized")

    # Construct a Credentials object from the access token
    credentials = Credentials(
        client_id=CLIENT_ID.value,
        token=backend_authorization.get("accessToken"),
        refresh_token=backend_authorization.get("refreshToken"),
        token_uri="https://oauth2.googleapis.com/token",
        client_secret=CLIENT_SECRET.value,
    )

    # Build the Google Calendar API service
    service = build("calendar", "v3", credentials=credentials)

    return service


@https_fn.on_call()
def list_user_calendars(req: https_fn.CallableRequest) -> dict:
    if not req.auth:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.UNAUTHENTICATED, "Unauthorized"
        )

    user_id = req.auth.uid

    # Fetch provider_account_id from user's sync profile or frontend request
    provider_account_id = req.data.get("providerAccountId")
    if not provider_account_id:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INVALID_ARGUMENT, "Missing providerAccountId"
        )

    try:
        service = get_calendar_service(user_id, provider_account_id)
    except Exception as e:
        logger.error(f"Failed to get calendar service: {e}")
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL, f"Failed to get calendar service: {e}"
        )

    try:
        # TODO : move this to GoogleCalendarManager, and handle pagination
        calendars_result = service.calendarList().list().execute()
        calendars = calendars_result.get("items", [])

        return {"calendars": calendars}
    except Exception as e:
        logger.error(f"Failed to list calendars: {e}")
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL, f"Failed to list calendars: {e}"
        )


@https_fn.on_call()
def is_authorized(req: https_fn.CallableRequest) -> dict:
    if not req.auth:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.UNAUTHENTICATED, "Unauthorized"
        )

    user_id = req.auth.uid

    provider_account_id = req.data.get("providerAccountId")
    if not provider_account_id:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INVALID_ARGUMENT, "Missing providerAccountId"
        )

    db = firestore.client()

    backend_authorization = (
        db.collection("backendAuthorizations")
        .document(user_id + provider_account_id)
        .get()
    )

    if not backend_authorization.exists:
        return {"authorized": False}

    # TODO : Check if the access token is still valid

    return {"authorized": True}


@https_fn.on_call()
def create_new_calendar(req: https_fn.CallableRequest) -> dict:
    if not req.auth:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.UNAUTHENTICATED, "Unauthorized"
        )

    user_id = req.auth.uid

    # Fetch provider_account_id from user's sync profile or frontend request
    provider_account_id = req.data.get("providerAccountId")
    if not provider_account_id:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INVALID_ARGUMENT, "Missing providerAccountId"
        )

    try:
        service = get_calendar_service(user_id, provider_account_id)
    except Exception as e:
        logger.error(f"Failed to get calendar service: {e}")
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL, f"Failed to get calendar service: {e}"
        )

    calendar_name = req.data.get("summary", "New Calendar")
    calendar_description = req.data.get("description", "Created by Syncademic")
    calendar_body = {
        "summary": calendar_name,
        "description": calendar_description,
        # 'timeZone': 'UTC' # TODO : specify timeZone
        # TODO : colorId
    }

    try:
        return service.calendars().insert(body=calendar_body).execute()
    except Exception as e:
        logger.error(f"Failed to create calendar: {e}")
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL, f"Failed to create calendar: {e}"
        )


@on_document_created(
    document="users/{userId}/syncProfiles/{syncProfileId}",
    memory=options.MemoryOption.MB_512,
)  # type: ignore
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
        sync_trigger="on_create",
    )


@https_fn.on_call()
def request_sync(req: https_fn.CallableRequest) -> Any:
    if not req.auth:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.UNAUTHENTICATED, "Unauthorized"
        )

    sync_profile_id = req.data.get("syncProfileId")

    if not sync_profile_id:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INVALID_ARGUMENT, "Missing syncProfileId"
        )

    syncProfile = (
        firestore.client()
        .collection("users")
        .document(req.auth.uid)
        .collection("syncProfiles")
        .document(sync_profile_id)
        .get()
    )

    if not syncProfile.exists:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.NOT_FOUND, "Sync profile not found"
        )

    logger.info(f"Starting manual synchronization for {req.auth.uid}/{sync_profile_id}")

    _synchronize_now(req.auth.uid, sync_profile_id, sync_trigger="manual")


# Every day at 2:00 AM UTC
@scheduler_fn.on_schedule(schedule="0 2 * * *")
def scheduled_sync(event: Any):
    db = firestore.client()

    for sync_profile in db.collection_group("syncProfiles").stream():
        sync_profile_id = sync_profile.id
        user_id = sync_profile.reference.parent.parent.id

        logger.info(f"Synchronizing {user_id}/{sync_profile_id}")
        try:
            _synchronize_now(user_id, sync_profile_id, sync_trigger="scheduled")
        except Exception as e:
            logger.error(f"Failed to synchronize {user_id}/{sync_profile_id}: {e}")


def _synchronize_now(
    user_id: str,
    sync_profile_id: str,
    sync_trigger: Literal["on_create", "manual", "scheduled"],
):
    db = firestore.client()

    sync_profile_ref = (
        db.collection("users")
        .document(user_id)
        .collection("syncProfiles")
        .document(sync_profile_id)
    )

    doc = sync_profile_ref.get()

    # TODO: If no status.type ??

    status = doc.get("status")
    if status and (status.get("type") in ["inProgress", "deleting", "deleted"]):
        logger.info(f"Synchronization is {status.get('type')}, skipping")
        return

    # TODO: Check access token validity and refresh or send error if needed

    sync_profile_ref.update(
        {
            "status": {
                "type": "inProgress",
                "syncTrigger": sync_trigger,
            }
        }
    )

    # TODO create CalendarManager here. This will allow us to test the authorization
    # and avoid doing it in the synchronization function. and report the error to the user

    try:
        service = get_calendar_service(
            user_id=user_id,
            provider_account_id=doc.get("targetCalendar.providerAccountId"),
        )
    except Exception as e:
        sync_profile_ref.update(
            {
                "status": {
                    "type": "failed",  # TODO : Specify that it failed because of authorization
                    "message": f"Autorization failed: {e}",
                    "syncTrigger": sync_trigger,
                }
            }
        )
        logger.info(f"Failed to get calendar service: {e}")
        return

    try:
        perform_synchronization(
            syncProfileId=sync_profile_id,
            icsSourceUrl=doc.get("scheduleSource.url"),
            targetCalendarId=doc.get("targetCalendar.id"),
            service=service,
            syncTrigger=sync_trigger,
            middlewares=[TitlePrettifier, ExamPrettifier],
        )
    except Exception as e:
        sync_profile_ref.update(
            {
                "status": {
                    "type": "failed",
                    "message": f"Synchronization failed: {e}",
                    "syncTrigger": sync_trigger,
                }
            }
        )
        logger.info(f"Synchronization failed: {e}")
        return

    sync_profile_ref.update(
        {
            "status": {
                "type": "success",
                "syncTrigger": sync_trigger,
                "lastSuccessfulSync": firestore.firestore.SERVER_TIMESTAMP,
            },
        }
    )

    logger.info("Synchronization completed successfully")


@https_fn.on_call(memory=options.MemoryOption.MB_512)
def delete_sync_profile(req: https_fn.CallableRequest) -> Any:
    if not req.auth:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.UNAUTHENTICATED, "Unauthorized"
        )

    sync_profile_id = req.data.get("syncProfileId")

    if not sync_profile_id:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INVALID_ARGUMENT, "Missing syncProfileId"
        )

    sync_profile_ref = (
        firestore.client()
        .collection("users")
        .document(req.auth.uid)
        .collection("syncProfiles")
        .document(sync_profile_id)
    )

    doc = sync_profile_ref.get()

    if not doc.exists:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.NOT_FOUND, "Sync profile not found"
        )

    status = doc.get("status")

    if status and (status.get("type") in ["deleting", "deleted"]):
        logger.info(f"Sync profile is already {status.get('type')}, skipping deletion")
        return

    sync_profile_ref.update(
        {
            "status": {
                "type": "deleting",
                "syncTrigger": None,
            }
        }
    )

    try:
        service = get_calendar_service(
            user_id=req.auth.uid,
            provider_account_id=doc.get("targetCalendar.providerAccountId"),
        )
    except Exception as e:
        logger.info(f"Failed to get calendar service: {e}. Skipping deletion")
        sync_profile_ref.update(
            {
                "status": {
                    "type": "deletionFailed",
                    "message": f"Autorization failed: {e}",
                }
            }
        )
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL,
            f"Authorization failed {e}",
        )

    calendar_manager = GoogleCalendarManager(service, doc.get("targetCalendar.id"))

    try:
        events = calendar_manager.get_events_ids_from_sync_profile(
            sync_profile_id=sync_profile_id,
        )
        logger.info(f"Deleting {len(events)} events")

        calendar_manager.delete_events(events)
    except Exception as e:
        logger.error(f"Failed to delete events: {e}")
        sync_profile_ref.update(
            {
                "status": {
                    "type": "deletionFailed",
                    "message": f"Could not delete events: {e}",
                }
            }
        )
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL,
            f"Failed to delete events: {e}",
        )

    sync_profile_ref.delete()

    sync_profile_ref.update(
        {
            "status": {
                "type": "deleted",
            }
        }
    )

    logger.info("Sync profile deleted successfully")


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

    redirect_uri = request.data.get("redirectUri", "https://syncademic.io")
    if redirect_uri not in ["https://syncademic.io", "http://localhost:7357"]:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INVALID_ARGUMENT, "Invalid redirect URI"
        )

    provider = request.data.get("provider")

    if not provider or provider.lower() not in ["google"]:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INVALID_ARGUMENT, "Invalid provider"
        )

    user_id = request.auth.uid

    db = firestore.client()

    # verify that the user exists in firestore
    user_ref = db.collection("users").document(user_id)
    if not user_ref.get().exists:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.NOT_FOUND, "User document not found"
        )

    # https://www.reddit.com/r/webdev/comments/11w1e36/warning_oauth_scope_has_changed_from (Workaround)
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
            redirect_uri=redirect_uri,
        )

        flow.fetch_token(code=auth_code)

        credentials = flow.credentials
    except Exception as e:
        logger.error(
            f"An error occurred while exchanging the authorization code: {str(e)}"
        )
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL,
            f"An error occurred while exchanging the authorization code: {str(e)}",
        )

    # The logged-in user (request.auth.uid) can authorize the backend on multiple google accounts.
    # Thus we need to get the unique identifier of the authorized google account
    # We can get this from the ID token

    id_token = credentials.id_token  # type: ignore

    if not id_token:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL, "ID token not found"
        )

    try:
        id_info = verify_oauth2_token(
            id_token, requests.Request(), audience=CLIENT_ID.value
        )

    except Exception as e:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL,
            f"An error occurred while verifying the ID token: {str(e)}",
        )

    google_user_id = id_info.get("sub")
    if not google_user_id:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL, "Google user ID not found"
        )

    access_token = credentials.token
    refresh_token = credentials.refresh_token

    # TODO : separate into two collections : backendAuthorizations and providerAccounts
    db.collection("backendAuthorizations").document(user_id + google_user_id).set(
        {
            "userId": user_id,
            "provider": "google",
            "providerAccountId": google_user_id,
            "providerAccountEmail": id_info.get("email"),
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "expirationDate": credentials.expiry,
        }
    )

    return {"success": True}
