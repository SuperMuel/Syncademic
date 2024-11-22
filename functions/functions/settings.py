from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env.syncademic-36c18",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    RULES_BUILDER_LLM: str = Field(default="gpt-4o")

    CLIENT_ID: str = Field(default="mock-client-id")
    CLIENT_SECRET: str = Field(default="mock-client-secret")

    LOCAL_REDIRECT_URI: str = Field(default="http://localhost:7357")
    PRODUCTION_REDIRECT_URI: str = Field(default="https://app.syncademic.io")

    MAX_ICS_SIZE_BYTES: int = Field(default=1 * 1024 * 1024)  # 1 MB
    URL_ICS_SOURCE_TIMEOUT_S: int = Field(default=10)

    MAX_SYNCHRONIZATIONS_PER_DAY: int = Field(
        default=24 * 5  # 24 syncs per day for 5 profiles
    )
    MAX_CLOUD_FUNCTIONS_INSTANCES: int = Field(default=10)


settings = Settings()

__all__ = ["settings"]
