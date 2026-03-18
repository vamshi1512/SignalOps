from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin, utcnow
from app.models.enums import SeverityLevel


class LogEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "log_events"

    service_id: Mapped[str] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    severity: Mapped[SeverityLevel] = mapped_column(Enum(SeverityLevel), index=True)
    message: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(120), default="application")
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    event_metadata: Mapped[dict[str, str]] = mapped_column("metadata", JSON, default=dict)
    fingerprint: Mapped[str] = mapped_column(String(255), index=True)
    anomaly_score: Mapped[float] = mapped_column(default=0.0)
    is_anomalous: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    service = relationship("Service", back_populates="logs")
