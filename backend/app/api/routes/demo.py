from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.db.session import get_session
from app.models.enums import UserRole
from app.schemas.common import ApiMessage
from app.services.demo import DemoService


router = APIRouter()


@router.post("/tick", response_model=ApiMessage)
async def run_demo_tick(
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.SRE)),
) -> ApiMessage:
    generated = await DemoService(session).generate_tick(burst=True)
    await session.commit()
    return ApiMessage(message=f"Generated {generated} demo log events")

