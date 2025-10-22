from contextlib import asynccontextmanager
from dataclasses import dataclass
import os
from pydantic import EmailStr, ValidationError
import json
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Any
import firebase_admin
from firebase_admin import credentials, auth, storage
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.ai.ruleset_builder import RulesetBuilder
from backend.bootstrap import bootstrap_event_bus
from backend.models import SyncTrigger
from backend.models.base import CamelCaseModel
from backend.models.schemas import (
    AuthorizeBackendInput,
    CreateSyncProfileInput,
    DeleteSyncProfileInput,
    IsAuthorizedInput,
    IsAuthorizedOutput,
    ListUserCalendarsInput,
    RequestSyncInput,
    ValidateIcsUrlInput,
    ValidateIcsUrlOutput,
)
from backend.repositories.backend_authorization_repository import (
    FirestoreBackendAuthorizationRepository,
)
from backend.repositories.sync_profile_repository import FirestoreSyncProfileRepository
from backend.repositories.sync_stats_repository import FirestoreSyncStatsRepository
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
from backend.logging_config import configure_logging
from backend.synchronizer.ics_cache import FirebaseIcsFileStorage
from backend.synchronizer.ics_source import UrlIcsSource
from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger("fastapi")

configure_logging(settings.LOG_LEVEL)

reusable_oauth2 = HTTPBearer(scheme_name="Firebase Token")


def initialize_firebase_app() -> None:
    """
    Initializes the Firebase Admin SDK.
    It first tries to use GOOGLE_APPLICATION_CREDENTIALS env var.
    """
    if firebase_admin._apps:  # already initialised
        return

    cred: credentials.Base | None
    if settings.FIREBASE_SERVICE_ACCOUNT_PATH is not None:
        logger.info("Initializing Firebase Admin SDK with service account file.")
        cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
    elif settings.FIREBASE_SERVICE_ACCOUNT_JSON is not None:
        logger.info("Initializing Firebase Admin SDK with service account JSON.")
        cred = credentials.Certificate(
            json.loads(settings.FIREBASE_SERVICE_ACCOUNT_JSON.get_secret_value())
        )
    else:
        logger.info(
            "Initializing Firebase Admin SDK with Application Default Credentials."
        )
        cred = credentials.ApplicationDefault()

    firebase_admin.initialize_app(cred)


@dataclass
class DomainServices:
    ics_service: IcsService
    authorization_service: AuthorizationService
    google_calendar_service: GoogleCalendarService
    sync_profile_service: SyncProfileService
    error_mapping: ErrorMapping


def build_domain_services() -> DomainServices:
    """Build backend domain services shared by FastAPI endpoints."""

    logger.info("Initializing domain services...")
    sync_stats_repo = FirestoreSyncStatsRepository()
    sync_profile_repo = FirestoreSyncProfileRepository()
    user_service = FirebaseAuthUserService()
    backend_auth_repo = FirestoreBackendAuthorizationRepository()

    dev_notification_service = create_dev_notification_service(
        user_service=user_service,
        sync_profile_repo=sync_profile_repo,
    )

    bucket = storage.bucket(settings.FIREBASE_STORAGE_BUCKET)
    ics_file_storage = FirebaseIcsFileStorage(bucket=bucket)

    event_bus = bootstrap_event_bus(
        ics_file_storage=ics_file_storage,
        dev_notification_service=dev_notification_service,
        sync_stats_repo=sync_stats_repo,
    )

    ics_service = IcsService(event_bus=event_bus)

    authorization_service = AuthorizationService(backend_auth_repo)
    google_calendar_service = GoogleCalendarService(authorization_service)

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

    error_mapping = ErrorMapping()
    logger.info("Domain services initialized.")

    return DomainServices(
        ics_service=ics_service,
        authorization_service=authorization_service,
        google_calendar_service=google_calendar_service,
        sync_profile_service=sync_profile_service,
        error_mapping=error_mapping,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201
    logger.info("Application startup: Initializing Firebase...")
    initialize_firebase_app()
    app.state.domain_services = build_domain_services()
    logger.info("Firebase initialized.")
    yield
    app.state.domain_services = None
    logger.info("Application shutdown.")


class UserInfo(CamelCaseModel):
    uid: str
    email: EmailStr | None = None
    display_name: str | None = None
    photo_url: str | None = None
    email_verified: bool = False


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(reusable_oauth2),
) -> UserInfo:
    """
    Dependency to get the current user from Firebase ID token.
    Verifies the token and returns user information.
    """

    try:
        decoded_token = auth.verify_id_token(token.credentials)

        return UserInfo(
            uid=decoded_token["uid"],
            email=decoded_token["email"],
            display_name=decoded_token.get("name"),
            photo_url=decoded_token.get("picture"),
            email_verified=decoded_token.get("email_verified", False),
        )

    except (
        auth.InvalidIdTokenError,
        auth.ExpiredIdTokenError,
        auth.RevokedIdTokenError,
        auth.CertificateFetchError,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase ID token: {e}",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        )
    except Exception as e:
        logger.error("An unexpected error occurred during token verification: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not validate credentials: {e}",
        )


app = FastAPI(title="Syncademic API", version="0.1.0", lifespan=lifespan)


def get_domain_services(request: Request) -> DomainServices:
    services: DomainServices | None = getattr(
        request.app.state, "domain_services", None
    )
    if services is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Domain services are not available",
        )
    return services


def raise_syncademic_http_error(
    error: SyncademicError,
    *,
    error_mapping: ErrorMapping,
) -> None:
    """Convert a Syncademic domain error into an HTTPException."""
    status_code, message = error_mapping.to_fastapi_status_code_and_message(error)

    detail: dict[str, Any] = {"message": message}
    if error.details:
        detail["details"] = error.details

    logger.error(
        "Syncademic error mapped to HTTP response.",
        extra={
            "error_type": type(error).__name__,
            "status_code": status_code,
        },
    )

    raise HTTPException(status_code=status_code, detail=detail) from error


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
    if settings.ENV == "dev"
    else [settings.PRODUCTION_FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint providing basic API information and available endpoints."""
    return {
        "name": "Syncademic API",
        "version": "0.1.0",
        "endpoints": {"health": "/health", "docs": "/docs", "redoc": "/redoc"},
        "settings": settings.model_dump(),
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/secure", response_model=UserInfo)
async def secure_endpoint(
    current_user: UserInfo = Depends(get_current_user),
) -> UserInfo:
    """
    A secure endpoint that requires Firebase authentication.
    The `current_user` is injected by the `get_current_user` dependency.
    """
    return current_user


@app.post("/ics/validate", response_model=ValidateIcsUrlOutput)
def validate_ics_url_endpoint(
    payload: ValidateIcsUrlInput,
    current_user: UserInfo = Depends(get_current_user),
    services: DomainServices = Depends(get_domain_services),
) -> ValidateIcsUrlOutput:
    """Validate an ICS URL using the shared Syncademic domain services."""

    try:
        ics_source = UrlIcsSource.from_str(payload.url)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        ) from exc

    logger.info(
        "Validating ICS URL via FastAPI",
        extra={"user_id": current_user.uid, "url": payload.url},
    )

    result = services.ics_service.validate_ics_url(
        ics_source,
        metadata={"user_id": current_user.uid},
    )

    return result


@app.post("/calendars/list")
def list_user_calendars_endpoint(
    payload: ListUserCalendarsInput,
    current_user: UserInfo = Depends(get_current_user),
    services: DomainServices = Depends(get_domain_services),
) -> dict[str, Any]:
    """List calendars for the authenticated user."""

    logger.info(
        "Listing calendars via FastAPI.",
        extra={
            "user_id": current_user.uid,
            "provider_account_id": payload.provider_account_id,
        },
    )

    try:
        calendars = services.google_calendar_service.list_calendars(
            user_id=current_user.uid,
            provider_account_id=payload.provider_account_id,
        )
    except SyncademicError as exc:
        raise_syncademic_http_error(exc, error_mapping=services.error_mapping)

    return {"calendars": calendars}


@app.post("/authorization/status", response_model=IsAuthorizedOutput)
def is_authorized_endpoint(
    payload: IsAuthorizedInput,
    current_user: UserInfo = Depends(get_current_user),
    services: DomainServices = Depends(get_domain_services),
) -> IsAuthorizedOutput:
    """Check whether the authenticated user is authorized for a provider account."""

    logger.info(
        "Checking authorization via FastAPI.",
        extra={
            "user_id": current_user.uid,
            "provider_account_id": payload.provider_account_id,
        },
    )

    try:
        services.authorization_service.test_authorization(
            current_user.uid,
            payload.provider_account_id,
        )
    except SyncademicError as exc:
        logger.info(
            "Authorization test failed.",
            extra={
                "user_id": current_user.uid,
                "provider_account_id": payload.provider_account_id,
                "error_type": type(exc).__name__,
            },
        )
        return IsAuthorizedOutput(authorized=False)

    logger.info("Authorization successful via FastAPI.")
    return IsAuthorizedOutput(authorized=True)


@app.post("/sync/request")
def request_sync_endpoint(
    payload: RequestSyncInput,
    current_user: UserInfo = Depends(get_current_user),
    services: DomainServices = Depends(get_domain_services),
) -> dict[str, bool]:
    """Trigger synchronization for a user's Syncademic profile."""

    logger.info(
        "%s sync request received via FastAPI.",
        getattr(payload.sync_type, "value", str(payload.sync_type)),
        extra={
            "user_id": current_user.uid,
            "sync_profile_id": payload.sync_profile_id,
        },
    )

    try:
        services.sync_profile_service.synchronize(
            user_id=current_user.uid,
            sync_profile_id=payload.sync_profile_id,
            sync_trigger=SyncTrigger.MANUAL,
            sync_type=payload.sync_type,
        )
    except SyncademicError as exc:
        raise_syncademic_http_error(exc, error_mapping=services.error_mapping)

    return {"success": True}


@app.delete("/sync-profiles/{sync_profile_id}")
def delete_sync_profile_endpoint(
    sync_profile_id: str,
    current_user: UserInfo = Depends(get_current_user),
    services: DomainServices = Depends(get_domain_services),
) -> dict[str, bool]:
    """Delete a sync profile for the authenticated user."""

    logger.info(
        "Deleting sync profile via FastAPI.",
        extra={
            "user_id": current_user.uid,
            "sync_profile_id": sync_profile_id,
        },
    )

    try:
        services.sync_profile_service.delete_sync_profile(
            user_id=current_user.uid,
            sync_profile_id=sync_profile_id,
        )
    except SyncademicError as exc:
        raise_syncademic_http_error(exc, error_mapping=services.error_mapping)

    return {"success": True}


@app.post("/authorization/backend")
def authorize_backend_endpoint(
    payload: AuthorizeBackendInput,
    current_user: UserInfo = Depends(get_current_user),
    services: DomainServices = Depends(get_domain_services),
) -> dict[str, bool]:
    """Authorize backend access for a provider account via OAuth."""

    logger.info(
        "Authorizing backend via FastAPI.",
        extra={
            "user_id": current_user.uid,
            "redirect_uri": str(payload.redirect_uri),
            "provider_account_id": payload.provider_account_id,
        },
    )

    try:
        services.authorization_service.authorize_backend_with_auth_code(
            user_id=current_user.uid,
            auth_code=payload.auth_code,
            redirect_uri=payload.redirect_uri,
            provider_account_id=payload.provider_account_id,
        )
    except SyncademicError as exc:
        raise_syncademic_http_error(exc, error_mapping=services.error_mapping)

    return {"success": True}


@app.post("/sync-profiles")
def create_sync_profile_endpoint(
    payload: CreateSyncProfileInput,
    current_user: UserInfo = Depends(get_current_user),
    services: DomainServices = Depends(get_domain_services),
) -> dict[str, Any]:
    """Create a new sync profile for the authenticated user."""

    logger.info(
        "Creating sync profile via FastAPI.",
        extra={"user_id": current_user.uid},
    )

    try:
        sync_profile = services.sync_profile_service.create_sync_profile(
            current_user.uid,
            payload,
        )
    except SyncademicError as exc:
        raise_syncademic_http_error(exc, error_mapping=services.error_mapping)

    return sync_profile.model_dump(mode="json")
