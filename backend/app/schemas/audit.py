from __future__ import annotations

from datetime import datetime

from app.schemas.common import OrmModel


class AuditEntryRead(OrmModel):
    id: str
    actor_id: str | None
    actor_email: str | None
    action: str
    resource_type: str
    resource_id: str
    details: dict
    created_at: datetime
    message: str
