from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.dashboard import DashboardOverview
from app.services.dashboard import DashboardService


router = APIRouter()


@router.get("/overview", response_model=DashboardOverview)
async def overview(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> DashboardOverview:
    payload = await DashboardService(session).overview()
    return DashboardOverview.model_validate(payload)
