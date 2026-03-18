from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SIGNALOPS_", env_file=".env", extra="ignore")

    app_name: str = "SignalOps"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://signalops:signalops@db:5432/signalops"
    redis_url: str = "redis://redis:6379/0"
    jwt_secret: str = Field(default="signalops-dev-secret-change-me-2026", min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60 * 12
    metrics_enabled: bool = True
    seed_on_start: bool = True
    demo_mode: bool = True
    cors_origins: list[str] = ["http://localhost:5173"]
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
