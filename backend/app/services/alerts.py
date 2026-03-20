from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import ApiError
from app.models.alert import Alert
from app.models.enums import AlertSeverity, AlertStatus
from app.models.user import User
from app.services.audit import AuditService
from app.services.serializers import serialize_alert


class AlertService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_alerts(
        self,
        *,
        status: AlertStatus | None = None,
        severity: AlertSeverity | None = None,
        robot_id: str | None = None,
    ) -> list[dict]:
        query = (
            select(Alert)
            .options(selectinload(Alert.robot), selectinload(Alert.mission))
            .order_by(Alert.occurred_at.desc())
        )
        if status:
            query = query.where(Alert.status == status)
        if severity:
            query = query.where(Alert.severity == severity)
        if robot_id:
            query = query.where(Alert.robot_id == robot_id)
        result = await self.session.execute(query)
        return [serialize_alert(alert) for alert in result.scalars().all()]

    async def acknowledge(self, alert_id: str, actor: User, notes: str = "") -> dict:
        result = await self.session.execute(
            select(Alert)
            .where(Alert.id == alert_id)
            .options(selectinload(Alert.robot), selectinload(Alert.mission))
        )
        alert = result.scalar_one_or_none()
        if not alert:
            raise ApiError("alert_not_found", "Alert not found", status_code=404)
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.notes = notes or alert.notes
        alert.acknowledged_by_id = actor.id
        alert.acknowledged_at = datetime.now(timezone.utc)
        await self.session.flush()
        await AuditService(self.session).log(
            actor=actor,
            action="alert.acknowledge",
            resource_type="alert",
            resource_id=alert.id,
            message=f"Acknowledged {alert.type.value}",
            details={"robot_id": alert.robot_id},
        )
        return serialize_alert(alert)

    async def process_rollup(self) -> int:
        result = await self.session.execute(select(Alert).where(Alert.status == AlertStatus.OPEN))
        return len(result.scalars().all())
