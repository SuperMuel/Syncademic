from contextlib import asynccontextmanager
import os
from pydantic import EmailStr, ValidationError
import json
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Any
import firebase_admin
from firebase_admin import credentials, auth, storage
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.bootstrap import bootstrap_event_bus
from backend.models.base import CamelCaseModel
from backend.models.schemas import ValidateIcsUrlInput, ValidateIcsUrlOutput
from backend.repositories.sync_profile_repository import FirestoreSyncProfileRepository
from backend.repositories.sync_stats_repository import FirestoreSyncStatsRepository
from backend.services.dev_notification_service import create_dev_notification_service
from backend.services.ics_service import IcsService
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


ics_service: IcsService | None = None


def initialize_domain_services() -> None:
    """Initialize backend domain services shared by FastAPI endpoints."""

    global ics_service

    if ics_service is not None:
        return

    logger.info("Initializing domain services...")

    sync_stats_repo = FirestoreSyncStatsRepository()
    sync_profile_repo = FirestoreSyncProfileRepository()
    user_service = FirebaseAuthUserService()
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
    logger.info("Domain services initialized.")


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201
    logger.info("Application startup: Initializing Firebase...")
    initialize_firebase_app()
    initialize_domain_services()
    logger.info("Firebase initialized.")
    yield
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
async def validate_ics_url_endpoint(
    payload: ValidateIcsUrlInput,
    current_user: UserInfo = Depends(get_current_user),
) -> ValidateIcsUrlOutput:
    """Validate an ICS URL using the shared Syncademic domain services."""

    if ics_service is None:
        logger.error("ICS service not initialized")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ICS service is not available",
        )

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

    result = ics_service.validate_ics_url(
        ics_source,
        metadata={"user_id": current_user.uid},
    )

    return result
