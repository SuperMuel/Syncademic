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

    CLIENT_ID: str = Field(default=...)
    CLIENT_SECRET: str = Field(default=...)

    LOCAL_REDIRECT_URI: str = Field(default=...)
    PRODUCTION_REDIRECT_URI: str = Field(default=...)

    MAX_ICS_SIZE_CHARS: int = Field(default=1_000_000)
    MAX_SYNCHRONIZATIONS_PER_DAY: int = Field(
        default=24 * 5  # 24 syncs per day for 5 profiles
    )
    MAX_SYNC_PROFILES: int = Field(default=2)


settings = Settings()

__all__ = ["settings"]
