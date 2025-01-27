from typing import Any

from firebase_admin import initialize_app, storage
from firebase_functions import https_fn, logger, options, scheduler_fn
from firebase_functions.firestore_fn import (
    Event,
    on_document_created,
)
from google.cloud.firestore_v1.base_document import DocumentSnapshot
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
from functions.models.schemas import (
    AuthorizeBackendInput,
    CreateNewCalendarInput,
    DeleteSyncProfileInput,
    IsAuthorizedInput,
    IsAuthorizedOutput,
    ListUserCalendarsInput,
    RequestSyncInput,
    ValidateIcsUrlInput,
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
from functions.services.authorization_service import AuthorizationService
from functions.services.exceptions.base import SyncademicError
from functions.services.exceptions.mapping import ErrorMapping
from functions.services.google_calendar_service import GoogleCalendarService
from functions.services.ics_service import IcsService
from functions.services.sync_profile_service import SyncProfileService
from functions.settings import settings
from functions.synchronizer.google_calendar_manager import (
    GoogleCalendarManager,
)
from functions.synchronizer.ics_cache import FirebaseIcsFileStorage
from functions.synchronizer.ics_parser import IcsParser
from functions.synchronizer.ics_source import UrlIcsSource

initialize_app()

backend_auth_repo: IBackendAuthorizationRepository = (
    FirestoreBackendAuthorizationRepository()
)
sync_stats_repo: ISyncStatsRepository = FirestoreSyncStatsRepository()
sync_profile_repo: ISyncProfileRepository = FirestoreSyncProfileRepository()
authorization_service = AuthorizationService(backend_auth_repo)
google_calendar_service = GoogleCalendarService(authorization_service)
ics_service = IcsService()
sync_profile_service = SyncProfileService(
    sync_profile_repo=sync_profile_repo,
    sync_stats_repo=sync_stats_repo,
    authorization_service=authorization_service,
    ics_service=ics_service,
)

error_mapping = ErrorMapping()


def get_user_id_or_raise(req: https_fn.CallableRequest) -> str:
    """
    Get the user ID from the request, or raise an error if the request is not authenticated.
    """

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

    return ics_service.validate_ics_url(
        UrlIcsSource(url=request.url),
        # In case of error, we want to understand what went wrong by looking at the ICS file.
        save_to_storage=True,
    ).model_dump()


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

    try:
        calendars = google_calendar_service.list_calendars(
            user_id=user_id,
            provider_account_id=request.providerAccountId,
        )
        return {"calendars": calendars}
    except SyncademicError as e:
        raise error_mapping.to_http_error(e)


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

    try:
        authorization_service.test_authorization(user_id, provider_account_id)
    except SyncademicError as e:
        logger.error(f"Failed to test authorization: {e}")
        return IsAuthorizedOutput(authorized=False).model_dump()

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

    try:
        result = google_calendar_service.create_new_calendar(
            user_id=user_id,
            provider_account_id=request.providerAccountId,
            summary=request.summary,
            description=request.description,
            color_id=request.colorId,
        )
        return result
    except SyncademicError as e:
        raise error_mapping.to_http_error(e)


def _create_ai_ruleset(sync_profile: SyncProfile):
    logger.info(
        f"Creating AI ruleset for {sync_profile.user_id}/{sync_profile.id} ({sync_profile.title})"
    )

    model = settings.RULES_BUILDER_LLM

    logger.info(f"Using {model} model")
    llm = init_chat_model(model)

    ics_url = sync_profile.scheduleSource.url
    ics_str = UrlIcsSource(url=ics_url).get_ics_string()
    events = IcsParser().try_parse(ics_str=ics_str)

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
def on_sync_profile_created(event: Event[DocumentSnapshot]) -> None:
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
    sync_profile_service.synchronize(
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

    sync_profile_service.synchronize(
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
def scheduled_sync(event: Any) -> None:
    logger.info("Scheduled synchronization started")

    for sync_profile in sync_profile_repo.list_all_active_sync_profiles():
        sync_profile_id, user_id = sync_profile.id, sync_profile.user_id

        logger.info(f"Synchronizing {user_id}/{sync_profile_id} ({sync_profile.title})")
        try:
            sync_profile_service.synchronize(
                user_id=user_id,
                sync_profile_id=sync_profile_id,
                sync_trigger=SyncTrigger.SCHEDULED,
            )
        except Exception as e:
            logger.error(f"Failed to synchronize {user_id}/{sync_profile_id}: {e}")


@https_fn.on_call(
    memory=options.MemoryOption.MB_512,
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
)
def delete_sync_profile(req: https_fn.CallableRequest) -> Any:
    user_id = get_user_id_or_raise(req)

    try:
        request = DeleteSyncProfileInput.model_validate(req.data)
    except ValidationError as e:
        raise https_fn.HttpsError(https_fn.FunctionsErrorCode.INVALID_ARGUMENT, str(e))

    try:
        sync_profile_service.delete_sync_profile(
            user_id=user_id, sync_profile_id=request.syncProfileId
        )
        return {"success": True}
    except SyncademicError as e:
        raise error_mapping.to_http_error(e)


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

    try:
        authorization_service.authorize_backend_with_auth_code(
            user_id=user_id,
            auth_code=request.authCode,
            redirect_uri=request.redirectUri,
            provider_account_id=request.providerAccountId,
        )
    except SyncademicError as e:
        logger.error(f"Failed to authorize backend: {e}")
        raise error_mapping.to_http_error(e)

    return {"success": True}
