"""Typed application settings (env-driven, 12-factor)."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WI_", env_file=".env", extra="ignore")

    app_name: str = "Workflow Intel"
    environment: str = "development"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    # --- LLM layer ---------------------------------------------------------- #
    llm_enabled: bool = False
    llm_model: str = "claude-opus-4-8"
    # ANTHROPIC_API_KEY is read by the SDK directly; we only check presence.
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")

    # --- Orchestration ------------------------------------------------------ #
    use_langgraph: bool = False  # build a true LangGraph StateGraph when available

    # --- Persistence -------------------------------------------------------- #
    database_url: str | None = None  # postgresql+asyncpg://...  (None → in-memory)

    # --- Observability ------------------------------------------------------ #
    otel_enabled: bool = False
    otel_endpoint: str | None = None  # OTLP collector endpoint
    service_name: str = "workflow-intel"


@lru_cache
def get_settings() -> Settings:
    return Settings()
