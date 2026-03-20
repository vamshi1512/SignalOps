from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixins import UUIDPrimaryKeyMixin, utcnow


class MissionEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "mission_events"

    robot_id: Mapped[str] = mapped_column(ForeignKey("robots.id"), index=True)
    mission_id: Mapped[str | None] = mapped_column(ForeignKey("missions.id"), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(64), index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    message: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    robot = relationship("Robot", back_populates="events")
    mission = relationship("Mission", back_populates="events")
