from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.core.errors import ApiError
from app.db.session import get_session
from app.models.alerting import AlertRule
from app.models.enums import AlertStatus, UserRole
from app.models.user import User
from app.repositories.alerts import AlertRepository
from app.schemas.alerts import AlertRead, AlertRuleCreate, AlertRuleRead, SuppressRequest
from app.schemas.common import ListResponse
from app.services.alerts import AlertService


router = APIRouter()


@router.get("", response_model=ListResponse[AlertRead])
async def list_alerts(
    session: AsyncSession = Depends(get_session),
    status: AlertStatus | None = None,
) -> ListResponse[AlertRead]:
    items = await AlertRepository(session).list_alerts(status=status)
    return ListResponse(items=[AlertRead.model_validate(item) for item in items], total=len(items))


@router.get("/rules", response_model=ListResponse[AlertRuleRead])
async def list_rules(session: AsyncSession = Depends(get_session)) -> ListResponse[AlertRuleRead]:
    items = await AlertRepository(session).list_rules()
    return ListResponse(items=[AlertRuleRead.model_validate(item) for item in items], total=len(items))


@router.post("/rules", response_model=AlertRuleRead)
async def create_rule(
    payload: AlertRuleCreate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.SRE)),
) -> AlertRuleRead:
    rule = AlertRule(**payload.model_dump())
    repository = AlertRepository(session)
    await repository.add_rule(rule)
    await session.commit()
    created = next(item for item in await repository.list_rules() if item.id == rule.id)
    return AlertRuleRead.model_validate(created)


@router.post("/{alert_id}/acknowledge", response_model=AlertRead)
async def acknowledge_alert(
    alert_id: str,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(require_roles(UserRole.ADMIN, UserRole.SRE)),
) -> AlertRead:
    repository = AlertRepository(session)
    alert = await repository.get(alert_id)
    if not alert:
        raise ApiError("alert_not_found", "Alert not found", status_code=404)
    updated = await AlertService(session).acknowledge(alert, actor)
    await session.commit()
    refreshed = await repository.get(updated.id)
    return AlertRead.model_validate(refreshed)


@router.post("/{alert_id}/suppress", response_model=AlertRead)
async def suppress_alert(
    alert_id: str,
    payload: SuppressRequest,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(require_roles(UserRole.ADMIN, UserRole.SRE)),
) -> AlertRead:
    repository = AlertRepository(session)
    alert = await repository.get(alert_id)
    if not alert:
        raise ApiError("alert_not_found", "Alert not found", status_code=404)
    updated = await AlertService(session).suppress(alert, actor, payload.minutes)
    await session.commit()
    refreshed = await repository.get(updated.id)
    return AlertRead.model_validate(refreshed)
