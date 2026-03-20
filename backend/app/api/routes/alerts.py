from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_session
from app.models.enums import AlertSeverity, AlertStatus, UserRole
from app.models.user import User
from app.schemas.alerts import AlertAcknowledgeRequest, AlertRead
from app.schemas.common import ListResponse
from app.services.alerts import AlertService


router = APIRouter()


@router.get("", response_model=ListResponse[AlertRead])
async def list_alerts(
    status: AlertStatus | None = Query(default=None),
    severity: AlertSeverity | None = Query(default=None),
    robot_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> ListResponse[AlertRead]:
    alerts = await AlertService(session).list_alerts(status=status, severity=severity, robot_id=robot_id)
    return ListResponse(items=[AlertRead.model_validate(alert) for alert in alerts], total=len(alerts))


@router.post("/{alert_id}/acknowledge", response_model=AlertRead)
async def acknowledge_alert(
    alert_id: str,
    payload: AlertAcknowledgeRequest,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(require_roles(UserRole.ADMIN, UserRole.OPERATOR)),
) -> AlertRead:
    alert = await AlertService(session).acknowledge(alert_id, actor, payload.notes)
    await session.commit()
    return AlertRead.model_validate(alert)
