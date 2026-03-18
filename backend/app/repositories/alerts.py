from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.alerting import Alert, AlertRule
from app.models.enums import AlertStatus
from app.models.incident import Incident, IncidentNote


class AlertRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_rules(self) -> list[AlertRule]:
        result = await self.session.execute(
            select(AlertRule).options(selectinload(AlertRule.service)).order_by(AlertRule.name)
        )
        return list(result.scalars().unique().all())

    async def add_rule(self, rule: AlertRule) -> AlertRule:
        self.session.add(rule)
        await self.session.flush()
        return rule

    async def list_alerts(self, *, status: AlertStatus | None = None, limit: int = 100) -> list[Alert]:
        stmt = (
            select(Alert)
            .options(
                selectinload(Alert.service),
                selectinload(Alert.rule).selectinload(AlertRule.service),
                selectinload(Alert.incident).selectinload(Incident.service),
                selectinload(Alert.incident).selectinload(Incident.assignee),
                selectinload(Alert.incident).selectinload(Incident.notes).selectinload(IncidentNote.author),
            )
            .order_by(Alert.triggered_at.desc())
            .limit(limit)
        )
        if status:
            stmt = stmt.where(Alert.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get(self, alert_id: str) -> Alert | None:
        result = await self.session.execute(
            select(Alert)
            .where(Alert.id == alert_id)
            .options(
                selectinload(Alert.service),
                selectinload(Alert.rule).selectinload(AlertRule.service),
                selectinload(Alert.incident).selectinload(Incident.service),
                selectinload(Alert.incident).selectinload(Incident.assignee),
                selectinload(Alert.incident).selectinload(Incident.notes).selectinload(IncidentNote.author),
            )
        )
        return result.scalar_one_or_none()

    async def find_active_for_rule(self, rule_id: str) -> Alert | None:
        result = await self.session.execute(
            select(Alert).where(
                Alert.rule_id == rule_id,
                Alert.status.in_([AlertStatus.OPEN, AlertStatus.ACKNOWLEDGED, AlertStatus.ESCALATED]),
            )
        )
        return result.scalar_one_or_none()

    async def add(self, alert: Alert) -> Alert:
        self.session.add(alert)
        await self.session.flush()
        return alert

    async def volume_by_hour(self) -> list[tuple[datetime, int]]:
        dialect = self.session.bind.dialect.name if self.session.bind else "sqlite"
        if dialect == "postgresql":
            hour_bucket = func.date_trunc("hour", Alert.triggered_at)
        else:
            hour_bucket = func.strftime("%Y-%m-%d %H:00:00", Alert.triggered_at)
        result = await self.session.execute(
            select(hour_bucket, func.count(Alert.id)).group_by(hour_bucket).order_by(hour_bucket)
        )
        rows = []
        for bucket, count in result.all():
            if isinstance(bucket, str):
                rows.append((datetime.fromisoformat(bucket), int(count)))
            else:
                rows.append((bucket, int(count)))
        return rows

    async def open_count(self) -> int:
        result = await self.session.execute(
            select(func.count(Alert.id)).where(Alert.status.in_([AlertStatus.OPEN, AlertStatus.ESCALATED]))
        )
        return int(result.scalar_one() or 0)
