from functools import wraps
from typing import Any, Callable, TypeVar

from firebase_admin import initialize_app, storage, auth
from firebase_functions import https_fn, logger, options, scheduler_fn
from firebase_functions.firestore_fn import (
    Event,
    on_document_created,
)
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, ValidationError

from functions.ai.ruleset_builder import RulesetBuilder
from functions.ai.time_schedule_compressor import TimeScheduleCompressor
from functions.models import (
    SyncTrigger,
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
from functions.services.ai_ruleset_service import AiRulesetService
from functions.services.authorization_service import AuthorizationService
from functions.services.exceptions.base import SyncademicError
from functions.services.exceptions.mapping import ErrorMapping
from functions.services.google_calendar_service import GoogleCalendarService
from functions.services.ics_service import IcsService
from functions.services.sync_profile_service import SyncProfileService
from functions.settings import settings
from functions.synchronizer.ics_cache import FirebaseIcsFileStorage
from functions.synchronizer.ics_parser import IcsParser
from functions.synchronizer.ics_source import UrlIcsSource
from functions.services.dev_notification_service import create_dev_notification_service


initialize_app()

backend_auth_repo: IBackendAuthorizationRepository = (
    FirestoreBackendAuthorizationRepository()
)
sync_stats_repo: ISyncStatsRepository = FirestoreSyncStatsRepository()
sync_profile_repo: ISyncProfileRepository = FirestoreSyncProfileRepository()
authorization_service = AuthorizationService(backend_auth_repo)
google_calendar_service = GoogleCalendarService(authorization_service)
ics_file_storage = FirebaseIcsFileStorage(bucket=storage.bucket())
ics_service = IcsService(ics_storage=ics_file_storage)

dev_notification_service = create_dev_notification_service()

sync_profile_service = SyncProfileService(
    sync_profile_repo=sync_profile_repo,
    sync_stats_repo=sync_stats_repo,
    authorization_service=authorization_service,
    ics_service=ics_service,
    dev_notification_service=dev_notification_service,
)

ruleset_builder = RulesetBuilder(llm=settings.RULES_BUILDER_LLM)
ai_ruleset_service = AiRulesetService(
    ics_service=ics_service,
    sync_profile_repo=sync_profile_repo,
    ruleset_builder=ruleset_builder,
)
error_mapping = ErrorMapping()

logger.info(f"Settings: {settings}")


def get_user_id_or_raise(req: https_fn.CallableRequest) -> str:
    """
    Get the user ID from the request, or raise an error if the request is not authenticated.
    """

    if not req.auth or not req.auth.uid:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.UNAUTHENTICATED, "Unauthorized request."
        )
    return req.auth.uid


T = TypeVar("T", bound=BaseModel)


def validate_request(input_model: type[T]):
    """
    Decorator to validate and deserialize the input for an HTTPS callable function using a specified Pydantic model.

    This decorator first retrieves the user ID from the provided callable request using `get_user_id_or_raise`.
    It then validates the incoming request data against the given Pydantic model. If validation fails,
    an `https_fn.HttpsError` is raised with the INVALID_ARGUMENT error code. Otherwise, the decorated function
    is called with the extracted user ID and the validated model instance.

    This helps eliminate repetitive validation logic across different endpoints.

    Example usage:
        @validate_request(MyPydanticModel)
        def my_function(user_id: str, validated_data: MyPydanticModel) -> dict:
            # Function implementation

    Args:
        input_model: The Pydantic model class used to validate and deserialize the request data.

    Returns:
        Callable: A decorator that transforms a function expecting a user ID and a validated model instance
                  into one that accepts an HTTPS callable request.

    Raises:
        https_fn.HttpsError: If the incoming request data does not conform to the provided model.
    """

    def decorator(func: Callable[[str, T], Any]):
        @wraps(func)
        def wrapper(req: https_fn.CallableRequest):
            user_id = get_user_id_or_raise(req)

            try:
                request = input_model.model_validate(req.data)
            except ValidationError as e:
                raise https_fn.HttpsError(
                    https_fn.FunctionsErrorCode.INVALID_ARGUMENT, str(e)
                )

            return func(user_id, request)

        return wrapper

    return decorator


@https_fn.on_call(
    memory=options.MemoryOption.MB_512,
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
)
@validate_request(ValidateIcsUrlInput)
def validate_ics_url(user_id: str, request: ValidateIcsUrlInput) -> dict:
    return ics_service.validate_ics_url(
        UrlIcsSource(url=request.url),
        # In case of error, we want to understand what went wrong by looking at the ICS file.
        save_to_storage=True,
    ).model_dump()


@https_fn.on_call(
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
    memory=options.MemoryOption.MB_512,
)
@validate_request(ListUserCalendarsInput)
def list_user_calendars(user_id: str, request: ListUserCalendarsInput) -> dict:
    logger.info(f"Listing calendars for {user_id}")

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
@validate_request(IsAuthorizedInput)
def is_authorized(user_id: str, request: IsAuthorizedInput) -> dict:
    logger.info(f"Checking authorization for {user_id}")

    provider_account_id = request.providerAccountId

    try:
        authorization_service.test_authorization(user_id, provider_account_id)
    except SyncademicError as e:
        logger.info(f"Failed to test authorization: {e}")
        return IsAuthorizedOutput(authorized=False).model_dump()

    logger.info("Authorization successful")
    return IsAuthorizedOutput(authorized=True).model_dump()


@https_fn.on_call(
    memory=options.MemoryOption.MB_512,
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
)
@validate_request(CreateNewCalendarInput)
def create_new_calendar(user_id: str, request: CreateNewCalendarInput) -> dict:
    logger.info(f"Creating new calendar for {user_id}")

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

    # Notify developers about the new sync profile
    dev_notification_service.on_new_sync_profile(
        user_id=user_id, sync_profile_id=sync_profile_id, title=sync_profile.title
    )

    ai_ruleset_service.create_ruleset_for_sync_profile(
        sync_profile,
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
@validate_request(RequestSyncInput)
def request_sync(user_id: str, request: RequestSyncInput) -> Any:
    sync_profile_id = request.syncProfileId
    sync_type = request.syncType

    logger.info(f"{sync_type} Sync request received for {user_id}/{sync_profile_id}")

    try:
        sync_profile_service.synchronize(
            user_id=user_id,
            sync_profile_id=sync_profile_id,
            sync_trigger=SyncTrigger.MANUAL,
            sync_type=sync_type,
        )
    except SyncademicError as e:
        raise error_mapping.to_http_error(e)


# Every day at 2:00 AM and 6:00 AM UTC
@scheduler_fn.on_schedule(
    schedule="0 2,6 * * *",
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
@validate_request(DeleteSyncProfileInput)
def delete_sync_profile(user_id: str, request: DeleteSyncProfileInput) -> dict:
    logger.info(f"Deleting sync profile for {user_id}")

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
@validate_request(AuthorizeBackendInput)
def authorize_backend(user_id: str, request: AuthorizeBackendInput) -> dict:
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


@on_document_created(
    document="users/{userId}",
    memory=options.MemoryOption.MB_512,
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
)  # type: ignore
def on_user_created(event: Event[DocumentSnapshot]) -> None:
    user_id = event.params["userId"]
    logger.info(f"New user created: {user_id}")

    # Get user data from the document
    user_data = event.data.to_dict() or {}

    # Get additional user info from Firebase Auth if possible
    additional_data = {}
    try:
        firebase_user = auth.get_user(user_id)

        # Add key user information to the notification
        additional_data = {
            "email": firebase_user.email or user_data.get("email", "Not provided"),
            "display_name": firebase_user.display_name or "Not provided",
            "email_verified": "Yes" if firebase_user.email_verified else "No",
            "provider": firebase_user.provider_data[0].provider_id
            if firebase_user.provider_data
            else "Unknown",
        }
    except Exception as e:
        # If we can't get Firebase Auth user, just use document data
        logger.warn(f"Could not get Firebase Auth user: {str(e)}")
        if "email" in user_data:
            additional_data["email"] = user_data["email"]

    # Notify developers about the new user with all available information
    dev_notification_service.on_new_user(
        user_id=user_id, additional_data=additional_data
    )
