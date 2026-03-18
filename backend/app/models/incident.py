from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin, utcnow
from app.models.enums import IncidentStatus, ServiceEnvironment, SeverityLevel


class Incident(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "incidents"

    service_id: Mapped[str] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), index=True)
    assignee_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text, default="")
    root_cause_hint: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[IncidentStatus] = mapped_column(Enum(IncidentStatus), default=IncidentStatus.OPEN, index=True)
    severity: Mapped[SeverityLevel] = mapped_column(Enum(SeverityLevel), index=True)
    environment: Mapped[ServiceEnvironment] = mapped_column(Enum(ServiceEnvironment), index=True)
    group_key: Mapped[str] = mapped_column(String(255), index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    occurrence_count: Mapped[int] = mapped_column(Integer, default=1)
    affected_logs: Mapped[int] = mapped_column(Integer, default=1)
    current_error_rate: Mapped[float] = mapped_column(Float, default=0.0)
    health_impact: Mapped[float] = mapped_column(Float, default=0.0)

    service = relationship("Service", back_populates="incidents")
    assignee = relationship("User", back_populates="assigned_incidents")
    notes = relationship("IncidentNote", back_populates="incident", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="incident")


class IncidentNote(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "incident_notes"

    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    is_system: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    incident = relationship("Incident", back_populates="notes")
    author = relationship("User", back_populates="notes")

