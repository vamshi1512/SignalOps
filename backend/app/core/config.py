from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ROBOYARD_", env_file=".env", extra="ignore")

    app_name: str = "RoboYard Control"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://roboyard:roboyard@db:5432/roboyard_control"
    redis_url: str = "redis://redis:6379/0"
    jwt_secret: str = Field(default="roboyard-control-dev-secret-change-me-2026", min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60 * 12
    metrics_enabled: bool = True
    seed_on_start: bool = True
    demo_mode: bool = True
    deterministic_mode: bool = True
    simulator_tick_seconds: float = 1.0
    telemetry_flush_interval: int = 6
    cors_origins: list[str] = ["http://localhost:5173"]
    log_level: str = "INFO"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: list[str] | str) -> list[str]:
        if isinstance(value, str) and not value.startswith("["):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.upper()


@lru_cache
def get_settings() -> Settings:
    return Settings()
