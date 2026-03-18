from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import IncidentStatus, SeverityLevel
from app.models.incident import Incident, IncidentNote


class IncidentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, incident_id: str) -> Incident | None:
        result = await self.session.execute(
            select(Incident)
            .where(Incident.id == incident_id)
            .options(
                selectinload(Incident.service),
                selectinload(Incident.assignee),
                selectinload(Incident.notes).selectinload(IncidentNote.author),
                selectinload(Incident.alerts),
            )
        )
        return result.scalar_one_or_none()

    async def list_filtered(
        self,
        *,
        service_id: str | None = None,
        severity: SeverityLevel | None = None,
        status: IncidentStatus | None = None,
        environment: str | None = None,
        limit: int = 100,
    ) -> list[Incident]:
        stmt = (
            select(Incident)
            .options(
                selectinload(Incident.service),
                selectinload(Incident.assignee),
                selectinload(Incident.notes).selectinload(IncidentNote.author),
            )
            .order_by(Incident.last_seen_at.desc())
            .limit(limit)
        )
        if service_id:
            stmt = stmt.where(Incident.service_id == service_id)
        if severity:
            stmt = stmt.where(Incident.severity == severity)
        if status:
            stmt = stmt.where(Incident.status == status)
        if environment:
            stmt = stmt.where(Incident.environment == environment)
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_open_by_group_key(self, group_key: str) -> Incident | None:
        result = await self.session.execute(
            select(Incident)
            .where(Incident.group_key == group_key, Incident.status != IncidentStatus.RESOLVED)
            .options(selectinload(Incident.notes))
        )
        return result.scalar_one_or_none()

    async def add(self, incident: Incident) -> Incident:
        self.session.add(incident)
        await self.session.flush()
        return incident

    async def add_note(self, note: IncidentNote) -> IncidentNote:
        self.session.add(note)
        await self.session.flush()
        return note

    async def average_mttr_hours(self) -> float:
        dialect = self.session.bind.dialect.name if self.session.bind else "sqlite"
        if dialect == "postgresql":
            duration_expr = func.avg(func.extract("epoch", Incident.resolved_at - Incident.first_seen_at))
            result = await self.session.execute(select(duration_expr).where(Incident.resolved_at.is_not(None)))
            average_seconds = result.scalar_one()
            if average_seconds is None:
                return 0.0
            return round(float(average_seconds) / 3600.0, 2)
        resolved_duration = func.avg(func.julianday(Incident.resolved_at) - func.julianday(Incident.first_seen_at))
        result = await self.session.execute(select(resolved_duration).where(Incident.resolved_at.is_not(None)))
        average_days = result.scalar_one()
        if average_days is None:
            return 0.0
        return round(float(average_days) * 24.0, 2)

    async def open_count(self) -> int:
        stmt = select(func.count(Incident.id)).where(Incident.status != IncidentStatus.RESOLVED)
        result = await self.session.execute(stmt)
        return int(result.scalar_one() or 0)

    async def count_in_window(self, *, service_id: str, start_at: datetime, end_at: datetime) -> int:
        stmt = select(func.count(Incident.id)).where(
            Incident.service_id == service_id,
            Incident.first_seen_at >= start_at,
            Incident.first_seen_at <= end_at,
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one() or 0)
