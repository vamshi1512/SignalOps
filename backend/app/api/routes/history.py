from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.history import MissionReplayRead, RobotHistoryRead
from app.services.history import HistoryService


router = APIRouter()


@router.get("/robots/{robot_id}", response_model=RobotHistoryRead)
async def robot_history(
    robot_id: str,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> RobotHistoryRead:
    payload = await HistoryService(session).robot_history(robot_id)
    return RobotHistoryRead.model_validate(payload)


@router.get("/missions/{mission_id}/replay", response_model=MissionReplayRead)
async def mission_replay(
    mission_id: str,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> MissionReplayRead:
    payload = await HistoryService(session).mission_replay(mission_id)
    return MissionReplayRead.model_validate(payload)
