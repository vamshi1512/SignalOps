from __future__ import annotations

from sqlalchemy import Enum, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ServiceEnvironment, ServicePriority


class Service(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "services"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    owner: Mapped[str] = mapped_column(String(120))
    environment: Mapped[ServiceEnvironment] = mapped_column(Enum(ServiceEnvironment), index=True)
    priority: Mapped[ServicePriority] = mapped_column(Enum(ServicePriority), index=True)
    sla_target: Mapped[float] = mapped_column(Float, default=99.9)
    description: Mapped[str] = mapped_column(Text, default="")

    logs = relationship("LogEvent", back_populates="service", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="service", cascade="all, delete-orphan")
    alert_rules = relationship("AlertRule", back_populates="service", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="service", cascade="all, delete-orphan")

