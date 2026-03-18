from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.alerting import Alert
from app.models.enums import AlertStatus, IncidentStatus
from app.models.incident import Incident
from app.models.service import Service


class ServiceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[Service]:
        result = await self.session.execute(
            select(Service)
            .options(selectinload(Service.incidents), selectinload(Service.alerts))
            .order_by(Service.priority, Service.name)
        )
        return list(result.scalars().unique().all())

    async def get(self, service_id: str) -> Service | None:
        result = await self.session.execute(
            select(Service)
            .where(Service.id == service_id)
            .options(selectinload(Service.incidents), selectinload(Service.alerts))
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Service | None:
        result = await self.session.execute(select(Service).where(Service.slug == slug))
        return result.scalar_one_or_none()

    async def add(self, service: Service) -> Service:
        self.session.add(service)
        await self.session.flush()
        return service

    async def health_snapshot(self) -> list[tuple[str, int, int]]:
        stmt: Select = (
            select(
                Service.id,
                func.count(Incident.id).filter(Incident.status != IncidentStatus.RESOLVED),
                func.count(Alert.id).filter(Alert.status.in_([AlertStatus.OPEN, AlertStatus.ESCALATED])),
            )
            .join(Incident, Incident.service_id == Service.id, isouter=True)
            .join(Alert, Alert.service_id == Service.id, isouter=True)
            .group_by(Service.id)
        )
        result = await self.session.execute(stmt)
        return list(result.all())

