from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, log: AuditLog) -> AuditLog:
        self.session.add(log)
        await self.session.flush()
        return log

    async def list_recent(self, limit: int = 100) -> list[AuditLog]:
        result = await self.session.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit))
        return list(result.scalars().all())

