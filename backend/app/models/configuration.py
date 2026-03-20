from __future__ import annotations

from sqlalchemy import Boolean, Enum, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import WeatherState


class PlatformConfig(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "platform_config"

    name: Mapped[str] = mapped_column(String(64), unique=True, default="default")
    weather_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    demo_mode: Mapped[bool] = mapped_column(Boolean, default=True)
    deterministic_mode: Mapped[bool] = mapped_column(Boolean, default=True)
    rain_pause_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    low_battery_threshold: Mapped[float] = mapped_column(Float, default=24.0)
    collision_threshold: Mapped[float] = mapped_column(Float, default=0.65)
    geofence_tolerance_m: Mapped[float] = mapped_column(Float, default=4.0)
    simulator_tick_seconds: Mapped[float] = mapped_column(Float, default=1.0)
    current_weather: Mapped[WeatherState] = mapped_column(Enum(WeatherState, native_enum=False), default=WeatherState.CLEAR)
    weather_intensity: Mapped[float] = mapped_column(Float, default=0.12)
