from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.enums import WeatherState
from app.schemas.common import OrmModel


class PlatformConfigRead(OrmModel):
    id: str
    name: str
    weather_enabled: bool
    demo_mode: bool
    deterministic_mode: bool
    rain_pause_enabled: bool
    low_battery_threshold: float = Field(ge=0.0, le=100.0)
    collision_threshold: float = Field(ge=0.0, le=1.0)
    geofence_tolerance_m: float = Field(ge=0.0, le=100.0)
    simulator_tick_seconds: float = Field(ge=0.1, le=60.0)
    current_weather: WeatherState
    weather_intensity: float = Field(ge=0.0, le=1.0)


class PlatformConfigUpdate(BaseModel):
    weather_enabled: bool | None = None
    deterministic_mode: bool | None = None
    rain_pause_enabled: bool | None = None
    low_battery_threshold: float | None = Field(default=None, ge=0.0, le=100.0)
    collision_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    geofence_tolerance_m: float | None = Field(default=None, ge=0.0, le=100.0)
    simulator_tick_seconds: float | None = Field(default=None, ge=0.1, le=60.0)
    current_weather: WeatherState | None = None
    weather_intensity: float | None = Field(default=None, ge=0.0, le=1.0)
