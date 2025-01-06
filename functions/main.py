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
from google.oauth2.credentials import Credentials
from google.oauth2.id_token import verify_oauth2_token
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from langchain.chat_models import init_chat_model
from pydantic import ValidationError

from functions.ai.ruleset_builder import RulesetBuilder
from functions.ai.time_schedule_compressor import TimeScheduleCompressor
from functions.models import (
    SyncProfileStatus,
    SyncProfileStatusType,
    SyncTrigger,
    SyncType,
)
from functions.models.authorization import BackendAuthorization
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
from functions.models.sync_profile import SyncProfile
from functions.repositories.backend_authorization_repository import (
    FirestoreBackendAuthorizationRepository,
    IBackendAuthorizationRepository,
)
from functions.repositories.sync_profile_repository import (
    FirestoreSyncProfileRepository,
    ISyncProfileRepository,
)
from functions.repositories.sync_stats_repository import (
    FirestoreSyncStatsRepository,
    ISyncStatsRepository,
)
from functions.settings import settings
from functions.synchronizer.google_calendar_manager import (
    GoogleCalendarManager,
)
from functions.synchronizer.ics_cache import FirebaseIcsFileStorage
from functions.synchronizer.ics_parser import IcsParser
from functions.synchronizer.ics_source import UrlIcsSource
from functions.synchronizer.synchronizer import (
    perform_synchronization,
)

initialize_app()

backend_auth_repo: IBackendAuthorizationRepository = (
    FirestoreBackendAuthorizationRepository()
)
sync_stats_repo: ISyncStatsRepository = FirestoreSyncStatsRepository()
sync_profile_repo: ISyncProfileRepository = FirestoreSyncProfileRepository()


def get_calendar_service(user_id: str, provider_account_id: str):
    """
    Construct the Google Calendar API service for a given user and provider account.
    """

    if not user_id:
        raise ValueError("User ID is required")
    if not provider_account_id:
        raise ValueError("Provider account ID is required")

    logger.info(f"Getting calendar service for {user_id}/{provider_account_id}")

    authorization = backend_auth_repo.get_authorization(user_id, provider_account_id)
    if authorization is None:
        logger.info("Backend authorization not found")
        raise ValueError("Target calendar is not authorized")

    # Construct a Credentials object from the stored token
    credentials = Credentials(
        client_id=settings.CLIENT_ID,
        token=authorization.accessToken,
        refresh_token=authorization.refreshToken,
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

    if not backend_auth_repo.exists(user_id, provider_account_id):
        logger.info("Backend authorization not found")
        return IsAuthorizedOutput(authorized=False).model_dump()

    # TODO : Actually check if the token is expired or if the user has revoked the access
    # by making a request to the Google Calendar API

    logger.info("Authorization successful")
    return IsAuthorizedOutput(authorized=True).model_dump()


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

    calendar_name = request.summary
    calendar_description = request.description
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
                calendarId=result.get("id"), body={"colorId": color_id}
            ).execute()
        except Exception as e:
            logger.error(f"Failed to patch calendar list entry: {e}")

    return result


def _create_ai_ruleset(sync_profile: SyncProfile):
    logger.info(
        f"Creating AI ruleset for {sync_profile.user_id}/{sync_profile.id} ({sync_profile.title})"
    )

    model = settings.RULES_BUILDER_LLM

    logger.info(f"Using {model} model")
    llm = init_chat_model(model)

    ics_url = sync_profile.scheduleSource.url
    ics_str = UrlIcsSource(ics_url).get_ics_string()
    events = IcsParser().parse(ics_str=ics_str)

    compresser = TimeScheduleCompressor()
    compressed_schedule = compresser.compress(events)

    logger.info(
        f"Compressed schedule to {len(compressed_schedule)=} "
        f"({len(compressed_schedule)/len(ics_str)*100:.2f}% of original)"
    )

    logger.info(f"Creating AI ruleset for {sync_profile.user_id}/{sync_profile.id}")

    ruleset_builder = RulesetBuilder(llm=llm)
    output = ruleset_builder.generate_ruleset(
        compressed_schedule,
        metadata={
            "ics_url": ics_url,
            "user_id": sync_profile.user_id,
            "sync_profile_id": sync_profile.id,
        },
    )

    sync_profile_repo.update_ruleset(
        user_id=sync_profile.user_id,
        sync_profile_id=sync_profile.id,
        ruleset=output.ruleset,
    )

    logger.info(
        f"Succesfully created AI ruleset for {sync_profile.user_id}/{sync_profile.id}"
    )


@on_document_created(
    document="users/{userId}/syncProfiles/{syncProfileId}",
    memory=options.MemoryOption.MB_512,
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
)  # type: ignore
def on_sync_profile_created(event: Event[DocumentSnapshot]):
    logger.info(f"Sync profile created: {event.data}")

    # Only logged-in users can create sync profiles in their own collection. No need to check for auth.
    user_id = event.params["userId"]
    sync_profile_id = event.params["syncProfileId"]
    data = event.data.to_dict()

    assert data, "Sync Profile Document was just created : it should not be empty"

    # Add created_at field
    sync_profile_repo.update_created_at(
        user_id=user_id, sync_profile_id=sync_profile_id
    )

    # Validate document using Pydantic
    data["id"] = sync_profile_id
    data["user_id"] = user_id
    sync_profile = SyncProfile.model_validate(data)

    try:
        _create_ai_ruleset(sync_profile)
    except Exception as e:
        logger.error(f"Failed to create AI ruleset: {e}")
        sync_profile_repo.update_ruleset_error(
            user_id=user_id,
            sync_profile_id=sync_profile_id,
            error_str=f"{type(e).__name__}: {str(e)}",
        )

    # Initial synchronization
    _synchronize_now(
        user_id=user_id,
        sync_profile_id=sync_profile_id,
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

    profile = sync_profile_repo.get_sync_profile(user_id, sync_profile_id)
    if profile is None:
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

    for sync_profile in sync_profile_repo.list_all_active_sync_profiles():
        sync_profile_id, user_id = sync_profile.id, sync_profile.user_id

        logger.info(f"Synchronizing {user_id}/{sync_profile_id} ({sync_profile.title})")
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
    profile = sync_profile_repo.get_sync_profile(user_id, sync_profile_id)
    if profile is None:
        logger.error("Sync profile not found")
        return

    if profile.status in [
        SyncProfileStatusType.IN_PROGRESS,
        SyncProfileStatusType.DELETING,
        SyncProfileStatusType.DELETION_FAILED,
    ]:
        logger.info(f"Synchronization is {profile.status}, skipping")
        return

    in_progress_status = SyncProfileStatus(
        type=SyncProfileStatusType.IN_PROGRESS,
        syncTrigger=sync_trigger,
        syncType=sync_type,
    )

    sync_profile_repo.update_sync_profile_status(
        user_id, sync_profile_id, in_progress_status
    )

    sync_count = sync_stats_repo.get_daily_sync_count(user_id)
    logger.info(f"Sync count: {sync_count}" if sync_count else "First sync of the day")

    if sync_count >= settings.MAX_SYNCHRONIZATIONS_PER_DAY:
        logger.info(f"User {user_id} has reached the daily synchronization limit.")
        failed_status = SyncProfileStatus(
            type=SyncProfileStatusType.FAILED,
            message=f"Daily synchronization limit of {settings.MAX_SYNCHRONIZATIONS_PER_DAY} reached.",
            syncTrigger=sync_trigger,
            syncType=sync_type,
        )
        sync_profile_repo.update_sync_profile_status(
            user_id, sync_profile_id, failed_status
        )
        return  # Do not synchronize

    target_calendar = profile.targetCalendar
    provider_account_id = target_calendar.providerAccountId

    try:
        service = get_calendar_service(user_id, provider_account_id)
        calendar_manager = GoogleCalendarManager(service, target_calendar.id)
        calendar_manager.test_authorization()
    except Exception as e:
        failed_status = SyncProfileStatus(
            type=SyncProfileStatusType.FAILED,
            message=f"Authorization failed: {e}",
            syncTrigger=sync_trigger,
            syncType=sync_type,
        )
        sync_profile_repo.update_sync_profile_status(
            user_id, sync_profile_id, failed_status
        )
        logger.info(f"Failed to get calendar service: {e}")
        return

    try:
        ics_url = profile.scheduleSource.url
        perform_synchronization(
            sync_profile_id=sync_profile_id,
            sync_trigger=sync_trigger,
            ics_source=UrlIcsSource(ics_url),
            ics_parser=IcsParser(),
            ics_cache=FirebaseIcsFileStorage(storage.bucket()),
            calendar_manager=calendar_manager,
            sync_type=sync_type,
            ruleset=profile.ruleset,
        )
    except Exception as e:
        logger.info(f"Synchronization failed: {e}")
        failed_status = SyncProfileStatus(
            type=SyncProfileStatusType.FAILED,
            message=f"Synchronization failed: {e}",
            syncTrigger=sync_trigger,
            syncType=sync_type,
        )
        sync_profile_repo.update_sync_profile_status(
            user_id, sync_profile_id, failed_status
        )
        return

    # If successful, update status + increment syncCount
    success_status = SyncProfileStatus(
        type=SyncProfileStatusType.SUCCESS,
        syncTrigger=sync_trigger,
        syncType=sync_type,
    )
    sync_profile_repo.update_sync_profile_status(
        user_id, sync_profile_id, success_status
    )
    sync_profile_repo.update_last_successful_sync(user_id, sync_profile_id)

    sync_stats_repo.increment_sync_count(user_id)
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

    sync_profile = sync_profile_repo.get_sync_profile(user_id, sync_profile_id)
    if sync_profile is None:
        logger.info("Sync profile not found")
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.NOT_FOUND, "Sync profile not found"
        )

    match status_type := sync_profile.status.type:
        case SyncProfileStatusType.DELETING:
            logger.info(f"Sync profile is already {status_type}, skipping deletion")
            return
        case SyncProfileStatusType.IN_PROGRESS:
            raise https_fn.HttpsError(
                https_fn.FunctionsErrorCode.FAILED_PRECONDITION,
                "Sync profile is currently in progress",
            )
        case (
            SyncProfileStatusType.SUCCESS
            | SyncProfileStatusType.FAILED
            | SyncProfileStatusType.DELETION_FAILED
        ):
            # Allow deletion to proceed
            pass
        # Do not use a catch-all case ! We want a type error if a new status is not handled.

    sync_profile_repo.update_sync_profile_status(
        user_id, sync_profile_id, SyncProfileStatus(type=SyncProfileStatusType.DELETING)
    )

    try:
        service = get_calendar_service(
            user_id, sync_profile.targetCalendar.providerAccountId
        )
    except Exception as e:
        logger.info(f"Failed to get calendar service: {e}. Skipping deletion")
        sync_profile_repo.update_sync_profile_status(
            user_id=user_id,
            sync_profile_id=sync_profile_id,
            status=SyncProfileStatus(
                type=SyncProfileStatusType.DELETION_FAILED,
                message=f"Authorization failed: {e}",
            ),
        )

        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL,
            "Authorization failed",
        )

    calendar_manager = GoogleCalendarManager(service, sync_profile.targetCalendar.id)

    try:
        events = calendar_manager.get_events_ids_from_sync_profile(
            sync_profile_id=sync_profile_id,
        )
        logger.info(f"Deleting {len(events)} events")
        calendar_manager.delete_events(events)
    except Exception as e:
        logger.error(f"Failed to delete events: {e}")
        sync_profile_repo.update_sync_profile_status(
            user_id=user_id,
            sync_profile_id=sync_profile_id,
            status=SyncProfileStatus(
                type=SyncProfileStatusType.DELETION_FAILED,
                message=f"Failed to delete events: {e}",
            ),
        )

        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL, "Failed to delete events"
        )

    sync_profile_repo.delete_sync_profile(user_id, sync_profile_id)

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

    if not credentials.token:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.INTERNAL,
            "Authorization process did not return a valid token",
        )

    backend_auth_repo.set_authorization(
        BackendAuthorization(
            userId=user_id,
            provider="google",
            providerAccountId=google_user_id,
            providerAccountEmail=id_info.get("email"),
            accessToken=credentials.token,
            refreshToken=credentials.refresh_token,
            expirationDate=credentials.expiry,
        )
    )

    return {"success": True}
