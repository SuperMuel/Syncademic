import logging
import os
from datetime import datetime, timezone
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
from pydantic import ValidationError

from functions.ai.ruleset_builder import RulesetBuilder
from functions.ai.time_schedule_compressor import TimeScheduleCompressor
from functions.models import Ruleset
from functions.models.schemas import (
    AuthorizeBackendInput,
    CreateNewCalendarInput,
    DeleteSyncProfileInput,
    IsAuthorizedInput,
    IsAuthorizedOutput,
    ListUserCalendarsInput,
    RequestSyncInput,
    ValidateIcsUrlInput,
    ValidateIcsUrlOutput,
)
from functions.settings import settings
from functions.synchronizer.google_calendar_manager import (
    GoogleCalendarManager,
)
from functions.synchronizer.ics_cache import FirebaseIcsFileStorage
from functions.synchronizer.ics_parser import IcsParser
from functions.synchronizer.ics_source import UrlIcsSource
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

    logger.info(f"Getting calendar service for {user_id}/{provider_account_id}")

    db = firestore.client()

    backend_authorization = (
        db.collection("backendAuthorizations")
        .document(user_id + provider_account_id)
        .get()
    )

    if not backend_authorization.exists:
        logger.info("Backend authorization not found")
        raise ValueError("Target calendar is not authorized")

    # Construct a Credentials object from the access token
    credentials = Credentials(
        client_id=settings.CLIENT_ID,
        token=backend_authorization.get("accessToken"),
        refresh_token=backend_authorization.get("refreshToken"),
        token_uri="https://oauth2.googleapis.com/token",
        client_secret=settings.CLIENT_SECRET,
    )

    # TODO : refresh token if expired

    # Build the Google Calendar API service
    service = build("calendar", "v3", credentials=credentials)

    return service


def get_user_id_or_raise(req: https_fn.CallableRequest) -> str:
    if not req.auth or not req.auth.uid:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.UNAUTHENTICATED, "Unauthorized request."
        )
    return req.auth.uid


@https_fn.on_call(
    memory=options.MemoryOption.MB_512,
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
)
def validate_ics_url(req: https_fn.CallableRequest) -> dict:
    get_user_id_or_raise(req)

    try:
        request = ValidateIcsUrlInput.model_validate(req.data)
    except ValidationError as e:
        raise https_fn.HttpsError(https_fn.FunctionsErrorCode.INVALID_ARGUMENT, str(e))

    ics_url = request.url

    # Use UrlIcsSource to fetch the ICS file and validate content-type and size
    try:
        ics_source = UrlIcsSource(ics_url)
        content = ics_source.get_ics_string()
    except Exception as e:
        logging.info(f"Failed to fetch ICS file at URL '{ics_url}': {e}")
        return {"valid": False, "error": str(e)}

    # Content verification
    try:
        parser = IcsParser()
        events = parser.parse(ics_str=content)
    except Exception as e:
        logging.error(f"Invalid ICS content at URL '{ics_url}': {e}")
        return {"valid": False, "error": str(e)}

    # If everything is fine, return success
    logger.info(f"Successfully fetched ICS file at URL '{ics_url}'")

    return ValidateIcsUrlOutput(valid=True, nbEvents=len(events)).model_dump()


@https_fn.on_call(
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
    memory=options.MemoryOption.MB_512,
)
def list_user_calendars(req: https_fn.CallableRequest) -> dict:
    user_id = get_user_id_or_raise(req)

    logger.info(f"Listing calendars for {user_id}")

    try:
        request = ListUserCalendarsInput.model_validate(req.data)
    except ValidationError as e:
        raise https_fn.HttpsError(https_fn.FunctionsErrorCode.INVALID_ARGUMENT, str(e))

    provider_account_id = request.providerAccountId

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


@https_fn.on_call(
    memory=options.MemoryOption.MB_512,
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
)
def is_authorized(req: https_fn.CallableRequest) -> dict:
    user_id = get_user_id_or_raise(req)

    try:
        request = IsAuthorizedInput.model_validate(req.data)
    except ValidationError as e:
        raise https_fn.HttpsError(https_fn.FunctionsErrorCode.INVALID_ARGUMENT, str(e))

    provider_account_id = request.providerAccountId

    db = firestore.client()

    backend_authorization = (
        db.collection("backendAuthorizations")
        .document(user_id + provider_account_id)
        .get()
    )

    if not backend_authorization.exists:
        logger.info("Backend authorization not found")
        authorized = False

    # TODO : create service and use GoogleCalendarManager to test authorization here

    logger.info("Authorization successful")
    authorized = True

    return IsAuthorizedOutput(authorized=authorized).model_dump()


@https_fn.on_call(
    memory=options.MemoryOption.MB_512,
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
)
def create_new_calendar(req: https_fn.CallableRequest) -> dict:
    user_id = get_user_id_or_raise(req)

    try:
        request = CreateNewCalendarInput.model_validate(req.data)
    except ValidationError as e:
        raise https_fn.HttpsError(https_fn.FunctionsErrorCode.INVALID_ARGUMENT, str(e))

    provider_account_id = request.providerAccountId
    color_id = request.colorId

    logger.info(f"Creating new calendar for {user_id}/{provider_account_id}")

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

    model = settings.RULES_BUILDER_LLM

    logger.info(f"Using {model} model")
    llm = init_chat_model(model)

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

    ruleset_builder = RulesetBuilder(llm=llm)

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
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
)  # type: ignore
def on_sync_profile_created(event: Event[DocumentSnapshot]):
    logger.info(f"Sync profile created: {event.data}")

    doc = event.data.to_dict()

    assert doc is not None, "Sync Profile Document was just created, should not be None"

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
        sync_trigger=SyncTrigger.ON_CREATE,
    )


@https_fn.on_call(
    memory=options.MemoryOption.MB_512,
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
)
def request_sync(req: https_fn.CallableRequest) -> Any:
    user_id = get_user_id_or_raise(req)

    try:
        request = RequestSyncInput.model_validate(req.data)
    except ValidationError as e:
        raise https_fn.HttpsError(https_fn.FunctionsErrorCode.INVALID_ARGUMENT, str(e))

    sync_profile_id = request.syncProfileId
    sync_type = request.syncType

    logger.info(f"{sync_type} Sync request received for {user_id}/{sync_profile_id}")

    syncProfile = (
        firestore.client()
        .collection("users")
        .document(user_id)
        .collection("syncProfiles")
        .document(sync_profile_id)
        .get()
    )

    assert isinstance(syncProfile, DocumentSnapshot)

    if not syncProfile.exists:
        logger.error("Sync profile not found")
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.NOT_FOUND, "Sync profile not found"
        )

    _synchronize_now(
        user_id=user_id,
        sync_profile_id=sync_profile_id,
        sync_trigger=SyncTrigger.MANUAL,
        sync_type=sync_type,
    )


# Every day at 2:00 AM UTC
@scheduler_fn.on_schedule(
    schedule="0 2 * * *",
    memory=options.MemoryOption.MB_512,
    timeout_sec=3600,
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
)
def scheduled_sync(event: Any):
    logger.info("Scheduled synchronization started")
    db = firestore.client()

    for sync_profile in db.collection_group("syncProfiles").stream():
        sync_profile_id = sync_profile.id
        user_id = sync_profile.reference.parent.parent.id

        logger.info(f"Synchronizing {user_id}/{sync_profile_id}")
        try:
            _synchronize_now(
                user_id, sync_profile_id, sync_trigger=SyncTrigger.SCHEDULED
            )
        except Exception as e:
            logger.error(f"Failed to synchronize {user_id}/{sync_profile_id}: {e}")


def _synchronize_now(
    user_id: str,
    sync_profile_id: str,
    sync_trigger: SyncTrigger,
    sync_type: SyncType = SyncType.REGULAR,
):
    db = firestore.client()

    user_ref = db.collection("users").document(user_id)

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
    if status and (
        status.get("type") in ["inProgress", "deleting", "deleted"]
    ):  # TODO : extract to a should_skip(status)->bool function
        logger.info(f"Synchronization is {status.get('type')}, skipping")
        return

    # TODO: Check access token validity and refresh or send error if needed

    sync_profile_ref.update(
        {
            "status": {
                "type": "inProgress",
                "syncTrigger": sync_trigger.value,
                "syncType": sync_type.value,
                "updatedAt": firestore.firestore.SERVER_TIMESTAMP,
            }
        }
    )

    # Check if number of sync per day is not exceeded
    # Get current date in UTC
    current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sync_stats_ref = user_ref.collection("syncStats").document(current_date)
    assert isinstance(sync_stats_ref, DocumentReference)

    # Fetch today's synchronization stats
    sync_stats_doc = sync_stats_ref.get()
    if sync_stats_doc.exists:
        sync_stats = sync_stats_doc.to_dict()
        assert sync_stats is not None, "sync_stats should not be None since it exists"
        sync_count = sync_stats.get("syncCount", 0)
    else:
        sync_count = 0

    assert isinstance(sync_count, int) and sync_count >= 0

    logger.info(f"Sync count: {sync_count}" if sync_count else "First sync of the day")

    # Check if the user has reached the daily limit
    if sync_count >= settings.MAX_SYNCHRONIZATIONS_PER_DAY:
        logger.info(f"User {user_id} has reached the daily synchronization limit.")
        sync_profile_ref.update(
            {
                "status": {
                    "type": "failed",
                    "message": f"Daily synchronization limit of {settings.MAX_SYNCHRONIZATIONS_PER_DAY} reached.",
                    "syncTrigger": sync_trigger.value,
                    "syncType": sync_type.value,
                    "updatedAt": firestore.firestore.SERVER_TIMESTAMP,
                }
            }
        )
        return  # Exit without performing synchronization

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
                    "syncTrigger": sync_trigger.value,
                    "syncType": sync_type.value,
                    "updatedAt": firestore.firestore.SERVER_TIMESTAMP,
                }
            }
        )
        logger.info(f"Failed to get calendar service: {e}")
        return

    ruleset: Ruleset | None = None

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
                        "syncTrigger": sync_trigger.value,
                        "syncType": sync_type.value,
                        "updatedAt": firestore.firestore.SERVER_TIMESTAMP,
                    }
                }
            )
            return
        logger.info(f"Found {len(ruleset.rules)} rules in ruleset")

    try:
        perform_synchronization(
            sync_profile_id=sync_profile_id,
            sync_trigger=sync_trigger,
            ics_source=UrlIcsSource(doc.get("scheduleSource.url")),
            ics_parser=IcsParser(),
            ics_cache=FirebaseIcsFileStorage(storage.bucket()),
            calendar_manager=calendar_manager,
            sync_type=sync_type,
            ruleset=ruleset,
        )
    except Exception as e:
        sync_profile_ref.update(
            {
                "status": {
                    "type": "failed",
                    "message": f"Synchronization failed: {e}",
                    "syncTrigger": sync_trigger.value,
                    "syncType": sync_type.value,
                    "updatedAt": firestore.firestore.SERVER_TIMESTAMP,
                }
            }
        )
        logger.info(f"Synchronization failed: {e}")
        return

    sync_profile_ref.update(
        {
            "status": {
                "type": "success",
                "syncTrigger": sync_trigger.value,
                "syncType": sync_type.value,
                "updatedAt": firestore.firestore.SERVER_TIMESTAMP,
            },
            "lastSuccessfulSync": firestore.firestore.SERVER_TIMESTAMP,
        }
    )
    sync_stats_ref.set({"syncCount": firestore.firestore.Increment(1)}, merge=True)

    logger.info("Synchronization completed successfully")


@https_fn.on_call(
    memory=options.MemoryOption.MB_512,
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
)
def delete_sync_profile(
    req: https_fn.CallableRequest,
) -> Any:  # TODO : add 'force' argument
    user_id = get_user_id_or_raise(req)

    try:
        request = DeleteSyncProfileInput.model_validate(req.data)
    except ValidationError as e:
        raise https_fn.HttpsError(https_fn.FunctionsErrorCode.INVALID_ARGUMENT, str(e))

    sync_profile_id = request.syncProfileId

    sync_profile_ref = (
        firestore.client()
        .collection("users")
        .document(user_id)
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
            user_id=user_id,
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

    logger.info("Sync profile deleted successfully")


@https_fn.on_call(
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
    memory=options.MemoryOption.MB_512,
)
def authorize_backend(req: https_fn.CallableRequest) -> dict:
    user_id = get_user_id_or_raise(req)

    try:
        request = AuthorizeBackendInput.model_validate(req.data)
    except ValidationError as e:
        raise https_fn.HttpsError(https_fn.FunctionsErrorCode.INVALID_ARGUMENT, str(e))

    auth_code = request.authCode
    redirect_uri = request.redirectUri
    provider_account_id = request.providerAccountId

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
