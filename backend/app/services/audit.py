from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditEntry
from app.models.user import User


class AuditService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def log(
        self,
        *,
        actor: User | None,
        action: str,
        resource_type: str,
        resource_id: str,
        message: str,
        details: dict | None = None,
    ) -> AuditEntry:
        entry = AuditEntry(
            actor_id=actor.id if actor else None,
            actor_email=actor.email if actor else None,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            message=message,
            details=details or {},
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def list_entries(self) -> list[AuditEntry]:
        result = await self.session.execute(select(AuditEntry).order_by(AuditEntry.created_at.desc()))
        return list(result.scalars().all())
