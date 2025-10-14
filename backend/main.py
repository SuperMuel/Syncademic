import logging
from functools import wraps
from typing import Any, Callable, TypeVar

from firebase_admin import auth, initialize_app, storage
from firebase_functions import https_fn, options, scheduler_fn
from firebase_functions.firestore_fn import (
    Event,
    on_document_created,
)
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from pydantic import BaseModel, ValidationError

from backend.ai.ruleset_builder import RulesetBuilder
from backend.bootstrap import bootstrap_event_bus
from backend.logging_config import configure_firebase_functions_logging
from backend.models import (
    SyncTrigger,
)
from backend.models.schemas import (
    AuthorizeBackendInput,
    DeleteSyncProfileInput,
    IsAuthorizedInput,
    IsAuthorizedOutput,
    ListUserCalendarsInput,
    RequestSyncInput,
    ValidateIcsUrlInput,
    CreateSyncProfileInput,
)
from backend.repositories.backend_authorization_repository import (
    FirestoreBackendAuthorizationRepository,
    IBackendAuthorizationRepository,
)
from backend.repositories.sync_profile_repository import (
    FirestoreSyncProfileRepository,
    ISyncProfileRepository,
)
from backend.repositories.sync_stats_repository import (
    FirestoreSyncStatsRepository,
    ISyncStatsRepository,
)
from backend.services.ai_ruleset_service import AiRulesetService
from backend.services.authorization_service import AuthorizationService
from backend.services.dev_notification_service import create_dev_notification_service
from backend.services.exceptions.base import SyncademicError
from backend.services.exceptions.mapping import ErrorMapping
from backend.services.google_calendar_service import GoogleCalendarService
from backend.services.ics_service import IcsService
from backend.services.sync_profile_service import SyncProfileService
from backend.services.user_service import FirebaseAuthUserService
from backend.settings import settings
from backend.shared import domain_events
from backend.synchronizer.ics_cache import FirebaseIcsFileStorage
from backend.synchronizer.ics_source import UrlIcsSource

logger = logging.getLogger(__name__)

configure_firebase_functions_logging(settings.LOG_LEVEL)

logger.info("Settings: %s", settings)

initialize_app()

backend_auth_repo: IBackendAuthorizationRepository = (
    FirestoreBackendAuthorizationRepository()
)
sync_stats_repo: ISyncStatsRepository = FirestoreSyncStatsRepository()
sync_profile_repo: ISyncProfileRepository = FirestoreSyncProfileRepository()
authorization_service = AuthorizationService(backend_auth_repo)
google_calendar_service = GoogleCalendarService(authorization_service)
ics_file_storage = FirebaseIcsFileStorage(bucket=storage.bucket())
user_service = FirebaseAuthUserService()

dev_notification_service = create_dev_notification_service(
    user_service=user_service,
    sync_profile_repo=sync_profile_repo,
)

error_mapping = ErrorMapping()

event_bus = bootstrap_event_bus(
    ics_file_storage=ics_file_storage,
    dev_notification_service=dev_notification_service,
    sync_stats_repo=sync_stats_repo,
)

ics_service = IcsService(event_bus=event_bus)


ruleset_builder = RulesetBuilder(llm=settings.RULES_BUILDER_LLM)

ai_ruleset_service = AiRulesetService(
    ics_service=ics_service,
    sync_profile_repo=sync_profile_repo,
    ruleset_builder=ruleset_builder,
    event_bus=event_bus,
)

sync_profile_service = SyncProfileService(
    sync_profile_repo=sync_profile_repo,
    sync_stats_repo=sync_stats_repo,
    authorization_service=authorization_service,
    ics_service=ics_service,
    google_calendar_service=google_calendar_service,
    ai_ruleset_service=ai_ruleset_service,
    event_bus=event_bus,
)


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


def validate_request(input_model: type[T]):  # noqa: ANN201
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
    region=settings.CLOUD_FUNCTIONS_REGION,
)
@validate_request(ValidateIcsUrlInput)
def validate_ics_url(user_id: str, request: ValidateIcsUrlInput) -> dict:
    logger.info("Validating ICS URL.", extra={"user_id": user_id})
    return ics_service.validate_ics_url(
        UrlIcsSource.from_str(request.url),
        metadata={"user_id": user_id},
    ).model_dump()


@https_fn.on_call(
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
    memory=options.MemoryOption.MB_512,
    region=settings.CLOUD_FUNCTIONS_REGION,
)
@validate_request(ListUserCalendarsInput)
def list_user_calendars(user_id: str, request: ListUserCalendarsInput) -> dict:
    logger.info("Listing calendars.", extra={"user_id": user_id})

    try:
        calendars = google_calendar_service.list_calendars(
            user_id=user_id,
            provider_account_id=request.provider_account_id,
        )
        return {"calendars": calendars}
    except SyncademicError as e:
        logger.error(
            "Failed to list calendars: %s",
            e,
            extra={
                "user_id": user_id,
                "provider_account_id": request.provider_account_id,
                "error_type": type(e).__name__,
            },
        )
        raise error_mapping.to_http_error(e)


@https_fn.on_call(
    memory=options.MemoryOption.MB_512,
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
    region=settings.CLOUD_FUNCTIONS_REGION,
)
@validate_request(IsAuthorizedInput)
def is_authorized(user_id: str, request: IsAuthorizedInput) -> dict:
    logger.info("Checking authorization.", extra={"user_id": user_id})

    provider_account_id = request.provider_account_id

    try:
        authorization_service.test_authorization(user_id, provider_account_id)
    except SyncademicError as e:
        logger.info(
            "Failed to test authorization: %s",
            e,
            extra={
                "user_id": user_id,
                "provider_account_id": provider_account_id,
                "error_type": type(e).__name__,
            },
        )
        return IsAuthorizedOutput(authorized=False).model_dump()

    logger.info("Authorization successful")
    return IsAuthorizedOutput(authorized=True).model_dump()


@https_fn.on_call(
    memory=options.MemoryOption.MB_512,
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
    region=settings.CLOUD_FUNCTIONS_REGION,
)
@validate_request(RequestSyncInput)
def request_sync(user_id: str, request: RequestSyncInput) -> Any:
    sync_profile_id = request.sync_profile_id
    sync_type = request.sync_type

    logger.info(
        "%s Sync request received.",
        getattr(sync_type, "value", str(sync_type)),
        extra={
            "user_id": user_id,
            "sync_profile_id": sync_profile_id,
        },
    )

    try:
        sync_profile_service.synchronize(
            user_id=user_id,
            sync_profile_id=sync_profile_id,
            sync_trigger=SyncTrigger.MANUAL,
            sync_type=sync_type,
        )
    except SyncademicError as e:
        logger.error(
            "Failed to synchronize.",
            extra={
                "user_id": user_id,
                "sync_profile_id": sync_profile_id,
                "error_type": type(e).__name__,
            },
        )
        raise error_mapping.to_http_error(e)


@scheduler_fn.on_schedule(
    schedule=settings.SCHEDULED_SYNC_CRON_SCHEDULE,
    memory=options.MemoryOption.MB_512,
    timeout_sec=settings.SCHEDULED_SYNC_TIMEOUT_SEC,
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
    region="europe-west3",  # Frankfurt, Germany, because Cloud Scheduler is not available in Paris/europe-west9
)
def scheduled_sync(event: Any) -> None:
    logger.info("Scheduled synchronization started.")

    for sync_profile in sync_profile_repo.list_all_active_sync_profiles():
        sync_profile_id, user_id = sync_profile.id, sync_profile.user_id

        logger.info(
            "Synchronizing.",
            extra={
                "user_id": user_id,
                "sync_profile_id": sync_profile_id,
                "sync_profile_title": sync_profile.title,
            },
        )
        try:
            sync_profile_service.synchronize(
                user_id=user_id,
                sync_profile_id=sync_profile_id,
                sync_trigger=SyncTrigger.SCHEDULED,
            )
        except Exception as e:
            logger.error(
                "Failed to synchronize. %s",
                e,
                extra={
                    "user_id": user_id,
                    "sync_profile_id": sync_profile_id,
                    "error_type": type(e).__name__,
                },
            )


@https_fn.on_call(
    memory=options.MemoryOption.MB_512,
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
    region=settings.CLOUD_FUNCTIONS_REGION,
)
@validate_request(DeleteSyncProfileInput)
def delete_sync_profile(user_id: str, request: DeleteSyncProfileInput) -> dict:
    logger.info(
        "Deleting sync profile.",
        extra={
            "user_id": user_id,
            "sync_profile_id": request.sync_profile_id,
        },
    )

    try:
        sync_profile_service.delete_sync_profile(
            user_id=user_id, sync_profile_id=request.sync_profile_id
        )
        return {"success": True}
    except SyncademicError as e:
        logger.error(
            "Failed to delete sync profile.",
            extra={
                "user_id": user_id,
                "sync_profile_id": request.sync_profile_id,
                "error_type": type(e).__name__,
            },
        )
        raise error_mapping.to_http_error(e)


@https_fn.on_call(
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
    memory=options.MemoryOption.MB_512,
    region=settings.CLOUD_FUNCTIONS_REGION,
)
@validate_request(AuthorizeBackendInput)
def authorize_backend(user_id: str, request: AuthorizeBackendInput) -> dict:
    logger.info(
        "Authorizing backend.",
        extra={
            "user_id": user_id,
            "redirect_uri": str(request.redirect_uri),
            "provider_account_id": request.provider_account_id,
        },
    )
    try:
        authorization_service.authorize_backend_with_auth_code(
            user_id=user_id,
            auth_code=request.auth_code,
            redirect_uri=request.redirect_uri,
            provider_account_id=request.provider_account_id,
        )
    except SyncademicError as e:
        logger.error(
            "Failed to authorize backend.",
            extra={
                "user_id": user_id,
                "redirect_uri": str(request.redirect_uri),
                "provider_account_id": request.provider_account_id,
                "error_type": type(e).__name__,
            },
        )
        raise error_mapping.to_http_error(e)

    return {"success": True}


@on_document_created(
    document="users/{userId}",
    memory=options.MemoryOption.MB_512,
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
    region=settings.CLOUD_FUNCTIONS_REGION,
)  # type: ignore
def on_user_created(event: Event[DocumentSnapshot]) -> None:
    user_id = event.params["userId"]
    logger.info("New user created: %s", user_id)

    # Get user data from the document
    user_data = event.data.to_dict() or {}

    # Get additional user info from Firebase Auth if possible
    event_data = {}
    try:
        firebase_user = auth.get_user(user_id)

        # Add key user information to the notification
        event_data = {
            "email": firebase_user.email or user_data.get("email", "Not provided"),
            "display_name": firebase_user.display_name or "Not provided",
            "email_verified": "Yes" if firebase_user.email_verified else "No",
            "provider_id": firebase_user.provider_data[0].provider_id
            if firebase_user.provider_data
            else "Unknown",
        }
    except Exception as e:
        # If we can't get Firebase Auth user, just use document data
        logger.warning(
            "Could not get Firebase Auth user: %s",
            e,
            extra={
                "user_id": user_id,
                "error_type": type(e).__name__,
            },
        )
        if "email" in user_data:
            event_data["email"] = user_data["email"]

    event_bus.publish(
        domain_events.UserCreated(
            user_id=user_id,
            email=event_data.get("email"),
            display_name=event_data.get("display_name"),
            provider_id=event_data.get("provider_id"),
        )
    )


@https_fn.on_call(
    memory=options.MemoryOption.MB_512,
    max_instances=settings.MAX_CLOUD_FUNCTIONS_INSTANCES,
    region=settings.CLOUD_FUNCTIONS_REGION,
)
@validate_request(CreateSyncProfileInput)
def create_sync_profile(user_id: str, request: CreateSyncProfileInput) -> dict:
    logger.info(
        "User %s is creating a new sync profile.",
        user_id,
        extra={
            "user_id": user_id,
        },
    )
    try:
        sync_profile = sync_profile_service.create_sync_profile(user_id, request)
    except SyncademicError as e:
        logger.error(
            "Failed to create sync profile.",
            extra={
                "user_id": user_id,
                "error_type": type(e).__name__,
            },
        )
        raise error_mapping.to_http_error(e)

    return sync_profile.model_dump(mode="json")
