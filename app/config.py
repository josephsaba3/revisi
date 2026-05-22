from functools import lru_cache

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Brand Voice Auditor"
    public_site_url: str | None = None
    database_url: str = "sqlite:///./brand_voice_auditor.db"
    llm_provider: Literal["openai", "anthropic"] = "openai"
    llm_analysis_prompt: str | None = None
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.5"
    openai_reasoning_effort: Literal["minimal", "low", "medium", "high"] = "low"
    openai_analysis_prompt: str | None = None
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-6"
    anthropic_max_tokens: int = 12000
    anthropic_effort: Literal["", "low", "medium", "high", "max"] = "medium"
    anthropic_prompt_cache_enabled: bool = True
    anthropic_openai_fallback_enabled: bool = True
    request_timeout_seconds: float = 15.0
    firecrawl_api_key: str | None = None
    firecrawl_fallback_enabled: bool = True
    firecrawl_timeout_seconds: float = 25.0
    firecrawl_max_concurrency: int = 3
    firecrawl_min_extracted_lines: int = 6
    firecrawl_min_extracted_words: int = 80
    scan_rate_limit_count: int = 5
    scan_rate_limit_window_seconds: int = 600
    scan_rate_limit_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
