import logging
import os
from typing import Any

from firebase_admin import firestore, initialize_app, storage
from firebase_functions import https_fn, logger, options, scheduler_fn
from firebase_functions.firestore_fn import (
    Event,
    on_document_created,
)
from google.auth.transport import requests
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.document import DocumentReference
from google.oauth2.credentials import Credentials
from google.oauth2.id_token import verify_oauth2_token
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from langchain.chat_models import init_chat_model

from functions.settings import settings
from functions.ai.ruleset_builder import RulesetBuilder
from functions.ai.time_schedule_compressor import TimeScheduleCompressor
from functions.rules.models import Ruleset
from functions.synchronizer.google_calendar_manager import (
    GoogleCalendarManager,
)
from functions.synchronizer.ics_cache import FirebaseIcsFileStorage
from functions.synchronizer.ics_parser import IcsParser
from functions.synchronizer.ics_source import UrlIcsSource
from functions.synchronizer.middleware.insa_middleware import (
    CM_TD_TP_Middleware,
    ExamPrettifier,
    Insa5IFMiddleware,
    TitlePrettifier,
)
from functions.synchronizer.synchronizer import (
    SyncTrigger,
    SyncType,
    perform_synchronization,
)

initialize_app()


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
        client_id=settings.CLIENT_ID,
        token=backend_authorization.get("accessToken"),
        refresh_token=backend_authorization.get("refreshToken"),
        token_uri="https://oauth2.googleapis.com/token",
        client_secret=settings.CLIENT_SECRET,
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
            https_fn.FunctionsErrorCode.INTERNAL, "Failed to get calendar service."
        )

    try:
        # TODO : move this to GoogleCalendarManager, and handle pagination
        calendars_result = service.calendarList().list().execute()
        calendars = calendars_result.get("items", [])

        return {"calendars": calendars}
    except Exception as e:
        logger.error(f"Failed to list calendars: {e}")
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL, "Failed to list calendars."
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

    provider_account_id = req.data.get("providerAccountId")
    if not provider_account_id:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INVALID_ARGUMENT, "Missing providerAccountId"
        )

    # Validate colorId
    color_id = req.data.get("colorId")
    if (
        color_id is not None
        and not isinstance(color_id, int)
        or not 1 <= color_id <= 25
    ):
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
            "Invalid colorId. Must be an integer between 1 and 25.",
        )

    try:
        service = get_calendar_service(user_id, provider_account_id)
    except Exception as e:
        logger.error(f"Failed to get calendar service: {e}")
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL, "Failed to get calendar service."
        )

    calendar_name = req.data.get("summary", "New Calendar")
    calendar_description = req.data.get("description", "Created by Syncademic")
    calendar_body = {
        "summary": calendar_name,
        "description": calendar_description,
    }

    try:
        result = service.calendars().insert(body=calendar_body).execute()
    except Exception as e:
        logger.error(f"Failed to create calendar: {e}")
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL, "Failed to create calendar."
        )

    # Calendar color is a property of the calendar list entry, not the calendar itself
    if color_id is not None:
        try:
            service.calendarList().patch(
                calendarId=result.get("id"),
                body={"colorId": color_id},
            ).execute()
        except Exception as e:
            logger.error(f"Failed to patch calendar list entry: {e}")

    return result


def _create_ai_ruleset(sync_profile_ref: DocumentReference):
    logger.info(f"Creating AI ruleset for {sync_profile_ref.path}")

    llm = settings.RULES_BUILDER_LLM

    logger.info(f"Using {llm} model")
    gpt4o = init_chat_model(llm)

    doc = sync_profile_ref.get()
    if not doc.exists:
        logger.error("Sync profile not found")
        return

    ics_url = doc.get("scheduleSource.url")
    ics_str = UrlIcsSource(ics_url).get_ics_string()
    events = IcsParser().parse(ics_str=ics_str)

    compresser = TimeScheduleCompressor()
    compressed_schedule = compresser.compress(events)

    logger.info(
        f"Compressed schedule to {len(compressed_schedule)=} ({len(compressed_schedule)/len(ics_str)*100:.2f}% of original)"
    )

    logger.info(f"Creating AI ruleset for {sync_profile_ref.path}")

    ruleset_builder = RulesetBuilder(llm=gpt4o)

    output = ruleset_builder.generate_ruleset(
        compressed_schedule,
        metadata={
            "ics_url": ics_url,
            "sync_profile_id": sync_profile_ref.id,
        },
    )

    sync_profile_ref.update({"ruleset": output.ruleset.model_dump_json()})


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

    # Add created_at field
    sync_profile_ref = event.data.reference
    assert isinstance(sync_profile_ref, DocumentReference)

    sync_profile_ref.update({"created_at": firestore.firestore.SERVER_TIMESTAMP})

    try:
        _create_ai_ruleset(sync_profile_ref)
    except Exception as e:
        logger.error(f"Failed to create AI ruleset: {e}")
        sync_profile_ref.update({"ruleset_error": str(e)})

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

    sync_type = req.data.get("syncType", "regular")

    if sync_type not in ["regular", "full"]:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INVALID_ARGUMENT, "Invalid syncType"
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

    _synchronize_now(
        req.auth.uid, sync_profile_id, sync_trigger="manual", sync_type=sync_type
    )


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
    sync_trigger: SyncTrigger,
    sync_type: SyncType = "regular",
):
    db = firestore.client()

    sync_profile_ref = (
        db.collection("users")
        .document(user_id)
        .collection("syncProfiles")
        .document(sync_profile_id)
    )

    assert isinstance(sync_profile_ref, DocumentReference)

    doc = sync_profile_ref.get()
    if not doc.exists:
        logger.error("Sync profile not found")
        return

    data = doc.to_dict()
    assert data is not None

    status = doc.get("status")
    assert status, f"status field is required. {status=}"
    if status and (status.get("type") in ["inProgress", "deleting", "deleted"]):
        logger.info(f"Synchronization is {status.get('type')}, skipping")
        return

    # TODO: Check access token validity and refresh or send error if needed

    sync_profile_ref.update(
        {
            "status": {
                "type": "inProgress",
                "syncTrigger": sync_trigger,
                "syncType": sync_type,
            }
        }
    )

    try:
        service = get_calendar_service(
            user_id=user_id,
            provider_account_id=doc.get("targetCalendar.providerAccountId"),
        )
        calendar_manager = GoogleCalendarManager(
            service=service, calendar_id=doc.get("targetCalendar.id")
        )
        calendar_manager.test_authorization()
    except Exception as e:
        sync_profile_ref.update(
            {
                "status": {
                    "type": "failed",
                    "message": f"Autorization failed: {e}",
                    # TODO : implement a way to re-authorize from the frontend
                    "syncTrigger": sync_trigger,
                    "syncType": sync_type,
                }
            }
        )
        logger.info(f"Failed to get calendar service: {e}")
        return

    customizations = {}

    if ruleset_json := data.get("ruleset"):
        try:
            ruleset = Ruleset.model_validate_json(ruleset_json)
        except Exception as e:
            logger.error(f"Failed to validate ruleset: {e}")
            sync_profile_ref.update(
                {
                    "status": {
                        "type": "failed",
                        "message": f"Failed to validate ruleset: {e}",
                        "syncTrigger": sync_trigger,
                        "syncType": sync_type,
                    }
                }
            )
            return

        customizations["ruleset"] = ruleset
        logger.info(f"Found rules: {ruleset}")
    else:
        customizations["middlewares"] = [
            TitlePrettifier,
            ExamPrettifier,
            Insa5IFMiddleware,
            CM_TD_TP_Middleware,
        ]

    try:
        perform_synchronization(
            sync_profile_id=sync_profile_id,
            sync_trigger=sync_trigger,
            ics_source=UrlIcsSource(doc.get("scheduleSource.url")),
            ics_parser=IcsParser(),
            ics_cache=FirebaseIcsFileStorage(storage.bucket()),
            calendar_manager=calendar_manager,
            sync_type=sync_type,
            **customizations,
        )
    except Exception as e:
        sync_profile_ref.update(
            {
                "status": {
                    "type": "failed",
                    "message": f"Synchronization failed: {e}",
                    "syncTrigger": sync_trigger,
                    "syncType": sync_type,
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
                "syncType": sync_type,
                "lastSuccessfulSync": firestore.firestore.SERVER_TIMESTAMP,
            },
        }
    )

    logger.info("Synchronization completed successfully")


@https_fn.on_call(memory=options.MemoryOption.MB_512)
def delete_sync_profile(
    req: https_fn.CallableRequest,
) -> Any:  # TODO : add 'force' argument
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
            "Authorization failed",
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
                    "message": "Could not delete events",
                }
            }
        )
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL,
            "Failed to delete events",
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

    redirect_uri = request.data.get("redirectUri", settings.PRODUCTION_REDIRECT_URI)
    if redirect_uri not in [
        settings.PRODUCTION_REDIRECT_URI,
        settings.LOCAL_REDIRECT_URI,
    ]:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
            f"{redirect_uri} is not a valid redirect URI.",
        )

    provider = request.data.get("provider")

    supported_providers = ["google"]

    if not provider or provider.lower() not in supported_providers:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
            f"Invalid provider. Supported providers are {supported_providers}",
        )

    provider_account_id = request.data.get("providerAccountId")

    if not provider_account_id:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INVALID_ARGUMENT, "Missing providerAccountId"
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
                    "client_id": settings.CLIENT_ID,
                    "client_secret": settings.CLIENT_SECRET,
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
            "An error occurred while exchanging the authorization code",
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
            id_token, requests.Request(), audience=settings.CLIENT_ID
        )

    except Exception as e:
        logger.error(f"An error occurred while verifying the ID token: {e}")
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL,
            "An error occurred while verifying the ID token",
        )

    google_user_id = id_info.get("sub")
    if not google_user_id:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL,
            "google_user_id not found in id_token",
        )

    # Check if the user is authorizing the backend on the correct google account
    if google_user_id != provider_account_id:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.PERMISSION_DENIED,
            "The authorized Google account does not match the providerAccountId (ProviderUserIdMismatch)",
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
