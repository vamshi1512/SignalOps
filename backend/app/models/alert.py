from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixins import UUIDPrimaryKeyMixin, utcnow
from app.models.enums import AlertSeverity, AlertStatus, AlertType


class Alert(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "alerts"

    robot_id: Mapped[str] = mapped_column(ForeignKey("robots.id"), index=True)
    mission_id: Mapped[str | None] = mapped_column(ForeignKey("missions.id"), nullable=True, index=True)
    zone_id: Mapped[str | None] = mapped_column(ForeignKey("zones.id"), nullable=True, index=True)
    acknowledged_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    type: Mapped[AlertType] = mapped_column(Enum(AlertType, native_enum=False), index=True)
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity, native_enum=False), index=True)
    status: Mapped[AlertStatus] = mapped_column(Enum(AlertStatus, native_enum=False), default=AlertStatus.OPEN, index=True)
    title: Mapped[str] = mapped_column(String(160))
    message: Mapped[str] = mapped_column(Text)
    notes: Mapped[str] = mapped_column(Text, default="")
    context: Mapped[dict] = mapped_column(JSON, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    robot = relationship("Robot", back_populates="alerts")
    mission = relationship("Mission", back_populates="alerts")
    zone = relationship("Zone", back_populates="alerts")
    acknowledged_by = relationship("User", back_populates="acknowledged_alerts")
