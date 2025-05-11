from contextlib import asynccontextmanager
import json
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from typing import Any
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.settings import Settings
from backend.logging_config import configure_logging
from dotenv import load_dotenv

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

    firebase_admin.initialize_app(cred)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201
    logger.info("Application startup: Initializing Firebase...")
    initialize_firebase_app()
    logger.info("Firebase initialized.")
    yield
    logger.info("Application shutdown.")


from pydantic import BaseModel, EmailStr


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
            uid=decoded_token.get("uid"),
            email=decoded_token.get("email"),
            display_name=decoded_token.get("name"),
            photo_url=decoded_token.get("picture"),
            email_verified=decoded_token.get("email_verified", False),
        )
    except auth.InvalidIdTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase ID token: {e}",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred during token verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not validate credentials",
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
