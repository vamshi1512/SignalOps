from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.db.session import get_session
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.config import PlatformConfigRead, PlatformConfigUpdate
from app.services.configuration import ConfigurationService


router = APIRouter()


@router.get("", response_model=PlatformConfigRead)
async def get_config(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.OPERATOR)),
) -> PlatformConfigRead:
    config = await ConfigurationService(session).get_or_create()
    return PlatformConfigRead.model_validate(config)


@router.patch("", response_model=PlatformConfigRead)
async def update_config(
    payload: PlatformConfigUpdate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> PlatformConfigRead:
    config = await ConfigurationService(session).update(payload)
    await session.commit()
    return PlatformConfigRead.model_validate(config)
