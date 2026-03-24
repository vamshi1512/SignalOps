from __future__ import annotations

from datetime import datetime
from typing import Any

from app.schemas.common import ORMModel


class AuditRead(ORMModel):
    id: str
    actor_id: str | None
    actor_email: str | None
    action: str
    resource_type: str
    resource_id: str
    details: dict[str, Any]
    created_at: datetime
    message: str
