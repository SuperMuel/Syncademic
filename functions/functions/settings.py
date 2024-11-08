from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os

IGNORE_ON_GITHUB_ACTIONS = "" if os.getenv("GITHUB_ACTIONS") else ...


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env.syncademic-36c18",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    RULES_BUILDER_LLM: str = Field(default="gpt-4o")

    CLIENT_ID: str = Field(default=IGNORE_ON_GITHUB_ACTIONS)
    CLIENT_SECRET: str = Field(default=IGNORE_ON_GITHUB_ACTIONS)

    LOCAL_REDIRECT_URI: str = Field(default=IGNORE_ON_GITHUB_ACTIONS)
    PRODUCTION_REDIRECT_URI: str = Field(default=IGNORE_ON_GITHUB_ACTIONS)

    MAX_ICS_SIZE_CHARS: int = Field(default=1_000_000)
    MAX_SYNCHRONIZATIONS_PER_DAY: int = Field(
        default=24 * 5  # 24 syncs per day for 5 profiles
    )
    MAX_CLOUD_FUNCTIONS_INSTANCES: int = Field(default=10)


settings = Settings()

__all__ = ["settings"]
