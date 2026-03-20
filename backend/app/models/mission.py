from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import MissionStatus, MissionType


class Mission(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "missions"

    name: Mapped[str] = mapped_column(String(160))
    robot_id: Mapped[str] = mapped_column(ForeignKey("robots.id"), index=True)
    zone_id: Mapped[str] = mapped_column(ForeignKey("zones.id"), index=True)
    mission_type: Mapped[MissionType] = mapped_column(Enum(MissionType, native_enum=False), index=True)
    status: Mapped[MissionStatus] = mapped_column(Enum(MissionStatus, native_enum=False), index=True)
    scheduled_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_duration_minutes: Mapped[float] = mapped_column(Float, default=45.0)
    progress_pct: Mapped[float] = mapped_column(Float, default=0.0)
    target_area_sqm: Mapped[float] = mapped_column(Float, default=0.0)
    completed_area_sqm: Mapped[float] = mapped_column(Float, default=0.0)
    command_queue: Mapped[list[dict]] = mapped_column(JSON, default=list)
    route_points: Mapped[list[dict[str, float]]] = mapped_column(JSON, default=list)
    replay_seed: Mapped[int] = mapped_column(default=0)
    operator_notes: Mapped[str] = mapped_column(Text, default="")

    robot = relationship("Robot", back_populates="missions")
    zone = relationship("Zone", back_populates="missions")
    telemetry = relationship("TelemetrySnapshot", back_populates="mission")
    events = relationship("MissionEvent", back_populates="mission")
    alerts = relationship("Alert", back_populates="mission")
