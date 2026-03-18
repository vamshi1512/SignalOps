from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import SeverityLevel
from app.models.log_event import LogEvent


class LogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, log_event: LogEvent) -> LogEvent:
        self.session.add(log_event)
        await self.session.flush()
        return log_event

    async def list_filtered(
        self,
        *,
        service_id: str | None = None,
        severity: SeverityLevel | None = None,
        environment: str | None = None,
        status: str | None = None,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        limit: int = 200,
    ) -> list[LogEvent]:
        stmt = select(LogEvent).options(selectinload(LogEvent.service)).order_by(LogEvent.occurred_at.desc()).limit(limit)
        if service_id:
            stmt = stmt.where(LogEvent.service_id == service_id)
        if severity:
            stmt = stmt.where(LogEvent.severity == severity)
        if start_at:
            stmt = stmt.where(LogEvent.occurred_at >= start_at)
        if end_at:
            stmt = stmt.where(LogEvent.occurred_at <= end_at)
        if environment:
            stmt = stmt.where(LogEvent.service.has(environment=environment))
        if status == "anomalous":
            stmt = stmt.where(LogEvent.is_anomalous.is_(True))
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get(self, log_id: str) -> LogEvent | None:
        result = await self.session.execute(
            select(LogEvent).where(LogEvent.id == log_id).options(selectinload(LogEvent.service))
        )
        return result.scalar_one_or_none()

    async def count_by_severity(
        self,
        *,
        service_id: str,
        severities: list[SeverityLevel],
        start_at: datetime,
        end_at: datetime,
    ) -> int:
        stmt = select(func.count(LogEvent.id)).where(
            LogEvent.service_id == service_id,
            LogEvent.occurred_at >= start_at,
            LogEvent.occurred_at <= end_at,
            LogEvent.severity.in_(severities),
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one() or 0)

    async def count_total(self, *, service_id: str, start_at: datetime, end_at: datetime) -> int:
        stmt = select(func.count(LogEvent.id)).where(
            LogEvent.service_id == service_id,
            LogEvent.occurred_at >= start_at,
            LogEvent.occurred_at <= end_at,
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one() or 0)

    async def count_anomalies(self, *, service_id: str, start_at: datetime, end_at: datetime) -> int:
        stmt = select(func.count(LogEvent.id)).where(
            LogEvent.service_id == service_id,
            LogEvent.occurred_at >= start_at,
            LogEvent.occurred_at <= end_at,
            LogEvent.is_anomalous.is_(True),
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one() or 0)

    async def bucket_by_hour(self, *, service_id: str | None, severity: SeverityLevel | None = None) -> list[tuple[datetime, int]]:
        dialect = self.session.bind.dialect.name if self.session.bind else "sqlite"
        if dialect == "postgresql":
            hour_bucket = func.date_trunc("hour", LogEvent.occurred_at)
        else:
            hour_bucket = func.strftime("%Y-%m-%d %H:00:00", LogEvent.occurred_at)
        stmt = select(hour_bucket, func.count(LogEvent.id)).group_by(hour_bucket).order_by(hour_bucket)
        if service_id:
            stmt = stmt.where(LogEvent.service_id == service_id)
        if severity:
            stmt = stmt.where(LogEvent.severity == severity)
        result = await self.session.execute(stmt)
        rows = []
        for bucket, count in result.all():
            if isinstance(bucket, str):
                rows.append((datetime.fromisoformat(bucket), int(count)))
            else:
                rows.append((bucket, int(count)))
        return rows
