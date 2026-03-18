from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin, utcnow
from app.models.enums import AlertMetric, AlertStatus, SeverityLevel


class AlertRule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "alert_rules"

    service_id: Mapped[str | None] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(140))
    description: Mapped[str] = mapped_column(Text, default="")
    metric: Mapped[AlertMetric] = mapped_column(Enum(AlertMetric), index=True)
    threshold: Mapped[float] = mapped_column(Float)
    window_minutes: Mapped[int] = mapped_column(Integer, default=15)
    severity: Mapped[SeverityLevel] = mapped_column(Enum(SeverityLevel))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    suppression_minutes: Mapped[int] = mapped_column(Integer, default=15)
    escalate_after_minutes: Mapped[int] = mapped_column(Integer, default=20)

    service = relationship("Service", back_populates="alert_rules")
    alerts = relationship("Alert", back_populates="rule", cascade="all, delete-orphan")


class Alert(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "alerts"

    rule_id: Mapped[str] = mapped_column(ForeignKey("alert_rules.id", ondelete="CASCADE"), index=True)
    service_id: Mapped[str] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), index=True)
    incident_id: Mapped[str | None] = mapped_column(ForeignKey("incidents.id"), nullable=True, index=True)
    status: Mapped[AlertStatus] = mapped_column(Enum(AlertStatus), default=AlertStatus.OPEN, index=True)
    message: Mapped[str] = mapped_column(Text)
    current_value: Mapped[float] = mapped_column(Float)
    threshold: Mapped[float] = mapped_column(Float)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    suppressed_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    escalation_level: Mapped[int] = mapped_column(Integer, default=0)

    rule = relationship("AlertRule", back_populates="alerts")
    service = relationship("Service", back_populates="alerts")
    incident = relationship("Incident", back_populates="alerts")

