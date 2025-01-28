from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, HttpUrl


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    RULES_BUILDER_LLM: str = Field(default="gpt-4o")

    CLIENT_ID: str = Field(default="mock-client-id")
    CLIENT_SECRET: str = Field(default="mock-client-secret")

    LOCAL_REDIRECT_URI: HttpUrl = Field(default=HttpUrl("http://localhost:7357"))
    """
    Local redirect URI, to use for testing.

    Warning : Pydantic automatically appends a slash at the end of the string when converting
    to str. You need to configure the allowed redirect URI in the Google Cloud Console
    WITHOUT a trailing slash.

    ```python
    url_str = str(settings.LOCAL_REDIRECT_URI)
    assert url_str.endswith("/")
    ```

    """

    PRODUCTION_REDIRECT_URI: HttpUrl = Field(
        default=HttpUrl("https://app.syncademic.io")
    )
    """
    Production redirect URI, to use for production.

    Warning : Pydantic automatically appends a slash at the end of the string when converting
    to str. You need to configure the allowed redirect URI in the Google Cloud Console WITH
    a trailing slash.

    ```python
    url_str = str(settings.PRODUCTION_REDIRECT_URI)
    assert url_str.endswith("/")
    ```
    """

    MAX_ICS_SIZE_BYTES: int = Field(default=1 * 1024 * 1024)  # 1 MB
    URL_ICS_SOURCE_TIMEOUT_S: int = Field(default=10)

    MAX_SYNCHRONIZATIONS_PER_DAY: int = Field(
        default=24 * 5  # 24 syncs per day for 5 profiles
    )
    MAX_CLOUD_FUNCTIONS_INSTANCES: int = Field(default=10)


settings = Settings()

__all__ = ["settings"]
