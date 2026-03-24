from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.common import ListResponse
from app.schemas.execution import NotificationRead
from app.services.notifications import NotificationService


router = APIRouter()


@router.get("/notifications", response_model=ListResponse[NotificationRead])
async def list_notifications(
    limit: int = Query(default=25, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> ListResponse[NotificationRead]:
    items = await NotificationService(session).list_notifications(limit=limit)
    return ListResponse(items=[NotificationRead.model_validate(item) for item in items], total=len(items))
