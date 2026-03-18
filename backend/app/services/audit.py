from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.user import User
from app.repositories.audit import AuditRepository


class AuditService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = AuditRepository(session)

    async def record(
        self,
        *,
        action: str,
        resource_type: str,
        resource_id: str,
        message: str,
        actor: User | None = None,
        details: dict[str, str] | None = None,
    ) -> AuditLog:
        log = AuditLog(
            actor_id=actor.id if actor else None,
            actor_email=actor.email if actor else None,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            message=message,
            details=details or {},
        )
        return await self.repository.add(log)

