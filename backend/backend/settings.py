from typing import Annotated, Literal, Self
import os
import json
from pydantic import (
    AfterValidator,
    Field,
    HttpUrl,
    SecretStr,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

RedirectUri = Annotated[HttpUrl, AfterValidator(lambda x: str(x).rstrip("/"))]
"""HttpUrl that serializes to string without trailing slash.

This is crucial for OAuth2 redirect URIs because:
1. OAuth2 providers do exact string matching on redirect URIs
2. A URI with a trailing slash is considered different from one without
3. The redirect URI we send in the initial auth request must exactly match
    the one we use to exchange the auth code for tokens

Example:
    "https://app.example.com" != "https://app.example.com/"

Without this, pydantic's HttpUrl may sometimes add a trailing slash during
serialization, causing the OAuth2 token exchange to fail with a redirect_uri_mismatch error.
"""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    RULES_BUILDER_LLM: str = Field(default="gpt-4o")

    CLIENT_ID: str = Field(default="mock-client-id")
    CLIENT_SECRET: SecretStr = Field(default=SecretStr("mock-client-secret"))

    OPENAI_API_KEY: SecretStr = Field(default=SecretStr("mock-openai-api-key"))

    LOCAL_REDIRECT_URI: RedirectUri = Field(default=HttpUrl("http://localhost:7357"))

    PRODUCTION_REDIRECT_URI: RedirectUri = Field(
        default=HttpUrl("https://app.syncademic.io")
    )

    PRODUCTION_FRONTEND_URL: str = Field(default="https://app.syncademic.io")

    MAX_ICS_SIZE_BYTES: int = Field(default=1 * 1024 * 1024)  # 1 MB
    URL_ICS_SOURCE_TIMEOUT_S: int = Field(default=10)

    MAX_SYNCHRONIZATIONS_PER_DAY: int = Field(
        default=24 * 5  # 24 syncs per day for 5 profiles
    )
    MAX_CLOUD_FUNCTIONS_INSTANCES: int = Field(default=10)
    CLOUD_FUNCTIONS_REGION: str = Field(default="europe-west9")

    # Scheduled sync configuration
    SCHEDULED_SYNC_CRON_SCHEDULE: str = Field(
        default="0 5 * * *",  # Every day at 5:00 AM UTC
        description="Cron schedule for automatic synchronization",
    )
    SCHEDULED_SYNC_TIMEOUT_SEC: int = Field(
        default=3600,
        description="Timeout in seconds before scheduled synchronization of all profiles is cancelled",
    )

    # Telegram notification settings
    TELEGRAM_BOT_TOKEN: SecretStr | None = Field(default=None)
    TELEGRAM_CHAT_ID: str | None = Field(default=None)
    TELEGRAM_MAX_TRACEBACK_LENGTH: int = Field(default=1000)

    # A size of 50 caused "The read operation timed out" errors,
    # so we're using a size of 25 for now.
    GOOGLE_API_BATCH_SIZE: int = Field(default=25)

    ENV: Literal["dev", "prod"] = Field(default="prod")

    FIREBASE_SERVICE_ACCOUNT_PATH: str | None = Field(
        default=None,
        examples=[
            "/local/path/to/firebase-service-account.json",
            None,
        ],
    )

    FIREBASE_SERVICE_ACCOUNT_JSON: SecretStr | None = Field(
        default=None,
        examples=[
            '{"type": "service_account", "project_id": "syncademic-36c18", "...": "..."}',
            None,
        ],
    )

    STORAGE_BUCKET: str | None = Field(None, description="Firebase Storage bucket name")

    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )

    @model_validator(mode="after")
    def validate_firebase_service_account(self) -> Self:
        if (
            self.FIREBASE_SERVICE_ACCOUNT_PATH is not None
            and self.FIREBASE_SERVICE_ACCOUNT_JSON is not None
        ):
            raise ValueError(
                "FIREBASE_SERVICE_ACCOUNT_PATH and FIREBASE_SERVICE_ACCOUNT_JSON cannot both be provided"
            )

        # Validate the file path exists if provided
        if self.FIREBASE_SERVICE_ACCOUNT_PATH is not None and not os.path.exists(
            self.FIREBASE_SERVICE_ACCOUNT_PATH
        ):
            raise ValueError(
                f"Firebase service account file does not exist at: {self.FIREBASE_SERVICE_ACCOUNT_PATH}"
            )

        # Validate JSON is properly formatted if provided
        if self.FIREBASE_SERVICE_ACCOUNT_JSON is not None:
            try:
                json.loads(self.FIREBASE_SERVICE_ACCOUNT_JSON.get_secret_value())
            except json.JSONDecodeError:
                raise ValueError("Firebase service account JSON is not valid JSON")

        return self


settings = Settings()

__all__ = ["settings"]
