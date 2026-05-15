from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Brand Voice Auditor"
    database_url: str = "sqlite:///./brand_voice_auditor.db"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.1-mini"
    request_timeout_seconds: float = 15.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
