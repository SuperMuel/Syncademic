from contextlib import asynccontextmanager
from pydantic import BaseModel, EmailStr
import json
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from typing import Any
import firebase_admin
from firebase_admin import credentials, auth, storage
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.ai.ruleset_builder import RulesetBuilder
from backend.bootstrap import bootstrap_event_bus
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
from backend.services.exceptions.mapping import ErrorMapping
from backend.services.google_calendar_service import GoogleCalendarService
from backend.services.sync_profile_service import SyncProfileService
from backend.services.user_service import FirebaseAuthUserService
from backend.settings import Settings
from backend.logging_config import configure_logging
from dotenv import load_dotenv
from backend.models.schemas import ValidateIcsUrlInput, ValidateIcsUrlOutput
from backend.services.ics_service import IcsService
from backend.synchronizer.ics_cache import FirebaseIcsFileStorage
from backend.synchronizer.ics_source import UrlIcsSource
from backend.infrastructure.event_bus import LocalEventBus

load_dotenv()


logger = logging.getLogger("fastapi")

settings = Settings()
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


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201
    logger.info("Application startup: Initializing Firebase...")
    initialize_firebase_app()
    logger.info("Firebase initialized.")

    # Initialize services and store them on app.state

    # Repositories
    app.state.backend_auth_repo = FirestoreBackendAuthorizationRepository()
    app.state.sync_stats_repo = FirestoreSyncStatsRepository()
    app.state.sync_profile_repo = FirestoreSyncProfileRepository()
    app.state.ics_file_storage = FirebaseIcsFileStorage(
        bucket=storage.bucket(settings.FIREBASE_STORAGE_BUCKET_NAME)
    )

    # Simpler Services
    app.state.user_service = FirebaseAuthUserService()
    app.state.authorization_service = AuthorizationService(app.state.backend_auth_repo)
    app.state.google_calendar_service = GoogleCalendarService(
        app.state.authorization_service
    )

    app.state.dev_notification_service = create_dev_notification_service(
        user_service=app.state.user_service,
        sync_profile_repo=app.state.sync_profile_repo,
    )

    # Event Bus (depends on other services/repos)
    app.state.event_bus = bootstrap_event_bus(
        ics_file_storage=app.state.ics_file_storage,
        dev_notification_service=app.state.dev_notification_service,
        sync_stats_repo=app.state.sync_stats_repo,
    )

    # Services depending on Event Bus or other services
    app.state.ics_service = IcsService(event_bus=app.state.event_bus)

    # AI Related Services
    app.state.ruleset_builder = RulesetBuilder(llm=settings.RULES_BUILDER_LLM)
    app.state.ai_ruleset_service = AiRulesetService(
        ics_service=app.state.ics_service,
        sync_profile_repo=app.state.sync_profile_repo,
        ruleset_builder=app.state.ruleset_builder,
        event_bus=app.state.event_bus,
    )

    # Main business logic service
    app.state.sync_profile_service = SyncProfileService(
        sync_profile_repo=app.state.sync_profile_repo,
        sync_stats_repo=app.state.sync_stats_repo,
        authorization_service=app.state.authorization_service,
        ics_service=app.state.ics_service,
        google_calendar_service=app.state.google_calendar_service,
        ai_ruleset_service=app.state.ai_ruleset_service,
        event_bus=app.state.event_bus,
    )

    logger.info("All services initialized.")
    yield
    logger.info("Application shutdown.")


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


# --- Dependency provider functions ---
def get_ics_service(request: Request) -> IcsService:
    return request.app.state.ics_service


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


@app.post("/validate-ics-url", response_model=ValidateIcsUrlOutput)
async def validate_ics_url(
    data: ValidateIcsUrlInput,
    current_user: UserInfo = Depends(get_current_user),
    ics_service: IcsService = Depends(get_ics_service),
) -> ValidateIcsUrlOutput:
    """
    Validates an ICS URL by attempting to fetch and parse its contents.

    Args:
        request: The request containing the ICS URL to validate
        current_user: The authenticated user

    Returns:
        ValidateIcsUrlOutput: A response containing the validation results
    """
    logger.info("Validating ICS URL.", extra={"user_id": current_user.uid})

    return ics_service.validate_ics_url(
        UrlIcsSource.from_str(data.url),
        metadata={"user_id": current_user.uid},
    )
