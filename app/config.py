from functools import lru_cache

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Brand Voice Auditor"
    database_url: str = "sqlite:///./brand_voice_auditor.db"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.5"
    openai_reasoning_effort: Literal["minimal", "low", "medium", "high"] = "low"
    openai_analysis_prompt: str | None = None
    request_timeout_seconds: float = 15.0
    scan_rate_limit_count: int = 5
    scan_rate_limit_window_seconds: int = 600
    scan_rate_limit_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
