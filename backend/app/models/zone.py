from __future__ import annotations

from sqlalchemy import Boolean, Enum, Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ZoneType


class Zone(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "zones"

    name: Mapped[str] = mapped_column(String(120), unique=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    zone_type: Mapped[ZoneType] = mapped_column(Enum(ZoneType, native_enum=False), default=ZoneType.PRIMARY, index=True)
    color: Mapped[str] = mapped_column(String(32), default="#22c55e")
    boundary: Mapped[list[dict[str, float]]] = mapped_column(JSON, default=list)
    charging_station: Mapped[dict[str, float]] = mapped_column(JSON, default=dict)
    task_areas: Mapped[list[dict]] = mapped_column(JSON, default=list)
    weather_exposure: Mapped[float] = mapped_column(Float, default=1.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    robots = relationship("Robot", back_populates="zone")
    missions = relationship("Mission", back_populates="zone")
    alerts = relationship("Alert", back_populates="zone")
