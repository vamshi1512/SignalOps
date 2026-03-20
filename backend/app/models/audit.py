from __future__ import annotations

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin


class AuditEntry(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "audit_entries"

    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    actor_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    resource_type: Mapped[str] = mapped_column(String(80), index=True)
    resource_id: Mapped[str] = mapped_column(String(64), index=True)
    message: Mapped[str] = mapped_column(String(255))
    details: Mapped[dict] = mapped_column(JSON, default=dict)

    actor = relationship("User", back_populates="audit_entries")
