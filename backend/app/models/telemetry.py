from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixins import UUIDPrimaryKeyMixin, utcnow
from app.models.enums import ConnectivityState, OperatingMode, RobotStatus, WeatherState


class TelemetrySnapshot(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "telemetry_snapshots"

    robot_id: Mapped[str] = mapped_column(ForeignKey("robots.id"), index=True)
    mission_id: Mapped[str | None] = mapped_column(ForeignKey("missions.id"), nullable=True, index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    position_x: Mapped[float] = mapped_column(Float)
    position_y: Mapped[float] = mapped_column(Float)
    battery_level: Mapped[float] = mapped_column(Float)
    speed_mps: Mapped[float] = mapped_column(Float)
    mission_progress_pct: Mapped[float] = mapped_column(Float, default=0.0)
    connectivity_state: Mapped[ConnectivityState] = mapped_column(Enum(ConnectivityState, native_enum=False))
    robot_status: Mapped[RobotStatus] = mapped_column(Enum(RobotStatus, native_enum=False))
    operating_mode: Mapped[OperatingMode] = mapped_column(Enum(OperatingMode, native_enum=False))
    weather_state: Mapped[WeatherState] = mapped_column(Enum(WeatherState, native_enum=False), default=WeatherState.CLEAR)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)

    robot = relationship("Robot", back_populates="telemetry")
    mission = relationship("Mission", back_populates="telemetry")
