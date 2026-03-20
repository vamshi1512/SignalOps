from __future__ import annotations

from sqlalchemy import Boolean, Enum, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import UserRole


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(255), default="Operations")
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, native_enum=False), index=True)
    theme_preference: Mapped[str] = mapped_column(String(50), default="dark")
    settings: Mapped[dict] = mapped_column(JSON, default=lambda: {"density": "comfortable", "alerts": True})
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    acknowledged_alerts = relationship("Alert", back_populates="acknowledged_by")
    audit_entries = relationship("AuditEntry", back_populates="actor")
