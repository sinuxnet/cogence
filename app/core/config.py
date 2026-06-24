from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    gitea_url: str
    gitea_token: str
    database_url: str
    api_secret_key: str

    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    atomic_commit_threshold: int = 10
    report_locale: str = "en"

    # Slice 4: only track repos from these Gitea organizations (comma-separated in env)
    gitea_organizations: list[str] = []
    # When gitea_organizations is set, also include personal (user-owned) repos if true
    gitea_include_personal: bool = False

    log_level: str = "INFO"
    log_file: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
