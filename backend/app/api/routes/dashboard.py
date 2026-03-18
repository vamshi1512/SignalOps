from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.dashboard import DashboardOverview
from app.services.dashboard import DashboardService


router = APIRouter()


@router.get("/overview", response_model=DashboardOverview)
async def overview(session: AsyncSession = Depends(get_session)) -> DashboardOverview:
    return await DashboardService(session).overview()

