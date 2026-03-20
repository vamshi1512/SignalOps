from __future__ import annotations

from datetime import datetime

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin, utcnow
from app.models.enums import ConnectivityState, OperatingMode, RobotStatus, RobotType


class Robot(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "robots"

    name: Mapped[str] = mapped_column(String(120), unique=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    robot_type: Mapped[RobotType] = mapped_column(Enum(RobotType, native_enum=False), index=True)
    model: Mapped[str] = mapped_column(String(120))
    serial: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    firmware_version: Mapped[str] = mapped_column(String(64), default="v3.4.1")
    status: Mapped[RobotStatus] = mapped_column(Enum(RobotStatus, native_enum=False), default=RobotStatus.IDLE, index=True)
    operating_mode: Mapped[OperatingMode] = mapped_column(
        Enum(OperatingMode, native_enum=False),
        default=OperatingMode.AUTONOMOUS,
    )
    connectivity_state: Mapped[ConnectivityState] = mapped_column(
        Enum(ConnectivityState, native_enum=False),
        default=ConnectivityState.ONLINE,
    )
    zone_id: Mapped[str] = mapped_column(ForeignKey("zones.id"), index=True)
    position_x: Mapped[float] = mapped_column(Float, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, default=0.0)
    heading_deg: Mapped[float] = mapped_column(Float, default=0.0)
    speed_mps: Mapped[float] = mapped_column(Float, default=0.0)
    battery_level: Mapped[float] = mapped_column(Float, default=100.0)
    signal_strength: Mapped[float] = mapped_column(Float, default=100.0)
    tool_state: Mapped[str] = mapped_column(String(64), default="standby")
    status_reason: Mapped[str] = mapped_column(Text, default="Awaiting mission dispatch")
    total_runtime_minutes: Mapped[float] = mapped_column(Float, default=0.0)
    total_distance_m: Mapped[float] = mapped_column(Float, default=0.0)
    charging_cycles: Mapped[int] = mapped_column(Integer, default=0)
    health_score: Mapped[float] = mapped_column(Float, default=98.0)
    deterministic_seed: Mapped[int] = mapped_column(Integer, default=0)
    last_seen_at: Mapped[datetime] = mapped_column(default=utcnow)

    zone = relationship("Zone", back_populates="robots")
    missions = relationship("Mission", back_populates="robot")
    telemetry = relationship("TelemetrySnapshot", back_populates="robot")
    events = relationship("MissionEvent", back_populates="robot")
    alerts = relationship("Alert", back_populates="robot")
