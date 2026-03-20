from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_session
from app.models.enums import MissionStatus, UserRole
from app.models.user import User
from app.schemas.common import ListResponse
from app.schemas.missions import MissionCommandRequest, MissionCreate, MissionDetail, MissionRead
from app.services.missions import MissionService
from app.services.serializers import serialize_mission


router = APIRouter()


@router.get("", response_model=ListResponse[MissionRead])
async def list_missions(
    status_filter: MissionStatus | None = Query(default=None, alias="status"),
    robot_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> ListResponse[MissionRead]:
    missions = await MissionService(session).list_missions(status=status_filter, robot_id=robot_id)
    return ListResponse(items=[MissionRead.model_validate(mission) for mission in missions], total=len(missions))


@router.post("", response_model=MissionRead, status_code=status.HTTP_201_CREATED)
async def create_mission(
    payload: MissionCreate,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(require_roles(UserRole.ADMIN, UserRole.OPERATOR)),
) -> MissionRead:
    mission = await MissionService(session).create_mission(payload, actor)
    await session.commit()
    return MissionRead.model_validate(mission)


@router.get("/{mission_id}", response_model=MissionDetail)
async def get_mission(
    mission_id: str,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> MissionDetail:
    mission = await MissionService(session).get_mission(mission_id)
    return MissionDetail.model_validate(serialize_mission(mission))


@router.post("/robots/{robot_id}/commands", response_model=MissionRead)
async def command_robot(
    robot_id: str,
    payload: MissionCommandRequest,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(require_roles(UserRole.ADMIN, UserRole.OPERATOR)),
) -> MissionRead:
    mission = await MissionService(session).command_robot(robot_id, payload.command, actor, payload.note)
    await session.commit()
    return MissionRead.model_validate(mission)
