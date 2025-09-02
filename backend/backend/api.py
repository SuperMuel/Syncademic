from contextlib import asynccontextmanager
from pydantic import BaseModel, EmailStr
import json
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from typing import Any

import firebase_admin
from firebase_admin import credentials, auth, initialize_app, storage

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.ai.ruleset_builder import RulesetBuilder
from backend.bootstrap import bootstrap_event_bus
from backend.models import SyncTrigger
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

from backend.settings import Settings
from backend.logging_config import configure_logging
from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger("fastapi")

settings = Settings()
configure_logging(settings.LOG_LEVEL)

reusable_oauth2 = HTTPBearer(scheme_name="Firebase Token")

error_mapping = ErrorMapping()

logger.info("Initializing services at module level.")


def initialize_firebase_app() -> None:
    """
    Initializes the Firebase Admin SDK.
    It first tries to use GOOGLE_APPLICATION_CREDENTIALS env var.
    """
    if firebase_admin._apps:  # already initialised
        return

    storage_bucket = os.getenv("STORAGE_BUCKET") or settings.STORAGE_BUCKET
    if not storage_bucket:
        raise ValueError("Storage bucket not specified in environment or settings.")

    cred: credentials.Base | None
    if settings.FIREBASE_SERVICE_ACCOUNT_PATH is not None:
        logger.info(f"Initializing Firebase Admin SDK with service account file.")
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

    firebase_admin.initialize_app(cred, options={"storageBucket": storage_bucket})


initialize_firebase_app()

backend_auth_repo = FirestoreBackendAuthorizationRepository()
sync_stats_repo = FirestoreSyncStatsRepository()
sync_profile_repo = FirestoreSyncProfileRepository()
authorization_service = AuthorizationService(backend_auth_repo)
google_calendar_service = GoogleCalendarService(authorization_service)
ics_file_storage = FirebaseIcsFileStorage(bucket=storage.bucket())
user_service = FirebaseAuthUserService()
dev_notification_service = create_dev_notification_service(
    user_service=user_service,
    sync_profile_repo=sync_profile_repo,
)
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

logger.info("Services initialized.")


class UserInfo(BaseModel):
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
        logger.error(f"An unexpected error occurred during token verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not validate credentials: {e}",
        )


app = FastAPI(title="Syncademic API", version="0.1.0")


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


@app.post("/validate-ics-url")
async def validate_ics_url(
    request: ValidateIcsUrlInput,
    current_user: UserInfo = Depends(get_current_user),
) -> dict:
    user_id = current_user.uid
    logger.info(f"Validating ICS URL.", extra={"user_id": user_id})
    try:
        return ics_service.validate_ics_url(
            UrlIcsSource.from_str(request.url),
            metadata={"user_id": user_id},
        ).model_dump()
    except SyncademicError as e:
        logger.error(
            f"Failed to validate ICS URL: {e}",
            extra={"user_id": user_id, "error_type": type(e).__name__},
        )
        status, detail = error_mapping.to_http_status_and_detail(e)
        raise HTTPException(status_code=status, detail=detail)


@app.post("/list-user-calendars")
async def list_user_calendars(
    request: ListUserCalendarsInput,
    current_user: UserInfo = Depends(get_current_user),
) -> dict:
    user_id = current_user.uid
    logger.info(f"Listing calendars.", extra={"user_id": user_id})
    try:
        calendars = google_calendar_service.list_calendars(
            user_id=user_id,
            provider_account_id=request.providerAccountId,
        )
        return {"calendars": calendars}
    except SyncademicError as e:
        logger.error(
            f"Failed to list calendars: {e}",
            extra={
                "user_id": user_id,
                "provider_account_id": request.providerAccountId,
                "error_type": type(e).__name__,
            },
        )
        status, detail = error_mapping.to_http_status_and_detail(e)
        raise HTTPException(status_code=status, detail=detail)


@app.post("/is-authorized")
async def is_authorized(
    request: IsAuthorizedInput,
    current_user: UserInfo = Depends(get_current_user),
) -> dict:
    user_id = current_user.uid
    provider_account_id = request.providerAccountId
    logger.info(f"Checking authorization.", extra={"user_id": user_id})
    try:
        authorization_service.test_authorization(user_id, provider_account_id)
    except SyncademicError as e:
        logger.info(
            f"Failed to test authorization: {e}",
            extra={
                "user_id": user_id,
                "provider_account_id": provider_account_id,
                "error_type": type(e).__name__,
            },
        )
        return IsAuthorizedOutput(authorized=False).model_dump()
    logger.info("Authorization successful")
    return IsAuthorizedOutput(authorized=True).model_dump()


@app.post("/request-sync")
async def request_sync(
    request: RequestSyncInput,
    current_user: UserInfo = Depends(get_current_user),
) -> dict:
    user_id = current_user.uid
    sync_profile_id = request.syncProfileId
    sync_type = request.syncType
    logger.info(
        f"{sync_type} Sync request received.",
        extra={"user_id": user_id, "sync_profile_id": sync_profile_id},
    )
    try:
        sync_profile_service.synchronize(
            user_id=user_id,
            sync_profile_id=sync_profile_id,
            sync_trigger=SyncTrigger.MANUAL,
            sync_type=sync_type,
        )
        return {"success": True}
    except SyncademicError as e:
        logger.error(
            f"Failed to synchronize.",
            extra={
                "user_id": user_id,
                "sync_profile_id": sync_profile_id,
                "error_type": type(e).__name__,
            },
        )
        status, detail = error_mapping.to_http_status_and_detail(e)
        raise HTTPException(status_code=status, detail=detail)


@app.post("/delete-sync-profile")
async def delete_sync_profile(
    request: DeleteSyncProfileInput,
    current_user: UserInfo = Depends(get_current_user),
) -> dict:
    user_id = current_user.uid
    logger.info(
        f"Deleting sync profile.",
        extra={"user_id": user_id, "sync_profile_id": request.syncProfileId},
    )
    try:
        sync_profile_service.delete_sync_profile(
            user_id=user_id, sync_profile_id=request.syncProfileId
        )
        return {"success": True}
    except SyncademicError as e:
        logger.error(
            f"Failed to delete sync profile.",
            extra={
                "user_id": user_id,
                "sync_profile_id": request.syncProfileId,
                "error_type": type(e).__name__,
            },
        )
        status, detail = error_mapping.to_http_status_and_detail(e)
        raise HTTPException(status_code=status, detail=detail)


@app.post("/authorize-backend")
async def authorize_backend(
    request: AuthorizeBackendInput,
    current_user: UserInfo = Depends(get_current_user),
) -> dict:
    user_id = current_user.uid
    logger.info(
        f"Authorizing backend.",
        extra={
            "user_id": user_id,
            "request": request.model_dump_json(),
            "redirect_uri": str(request.redirectUri),
            "provider_account_id": request.providerAccountId,
        },
    )
    try:
        authorization_service.authorize_backend_with_auth_code(
            user_id=user_id,
            auth_code=request.authCode,
            redirect_uri=request.redirectUri,
            provider_account_id=request.providerAccountId,
        )
        return {"success": True}
    except SyncademicError as e:
        logger.error(
            f"Failed to authorize backend.",
            extra={
                "user_id": user_id,
                "redirect_uri": str(request.redirectUri),
                "provider_account_id": request.providerAccountId,
                "error_type": type(e).__name__,
            },
        )
        status, detail = error_mapping.to_http_status_and_detail(e)
        raise HTTPException(status_code=status, detail=detail)


@app.post("/create-sync-profile")
async def create_sync_profile(
    request: CreateSyncProfileInput,
    current_user: UserInfo = Depends(get_current_user),
) -> dict:
    user_id = current_user.uid
    logger.info(
        f"User {user_id} is creating a new sync profile.",
        extra={"user_id": user_id, "request": request.model_dump_json()},
    )
    try:
        sync_profile = sync_profile_service.create_sync_profile(user_id, request)
        return sync_profile.model_dump(mode="json")
    except SyncademicError as e:
        logger.error(
            f"Failed to create sync profile.",
            extra={
                "user_id": user_id,
                "request": request.model_dump_json(),
                "error_type": type(e).__name__,
            },
        )
        status, detail = error_mapping.to_http_status_and_detail(e)
        raise HTTPException(status_code=status, detail=detail)
