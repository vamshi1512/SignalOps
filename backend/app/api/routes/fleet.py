from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_session
from app.models.enums import RobotStatus, UserRole
from app.models.user import User
from app.schemas.common import ListResponse, MessageResponse
from app.schemas.fleet import RobotCreate, RobotDetail, RobotRead, RobotUpdate, ZoneRead
from app.services.fleet import FleetService


router = APIRouter()


@router.get("/zones", response_model=ListResponse[ZoneRead])
async def list_zones(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> ListResponse[ZoneRead]:
    zones = await FleetService(session).list_zones()
    return ListResponse(items=[ZoneRead.model_validate(zone) for zone in zones], total=len(zones))


@router.get("/robots", response_model=ListResponse[RobotRead])
async def list_robots(
    search: str | None = Query(default=None),
    status_filter: RobotStatus | None = Query(default=None, alias="status"),
    zone_id: str | None = Query(default=None),
    battery_below: float | None = Query(default=None, ge=0.0, le=100.0),
    fault_only: bool = Query(default=False),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> ListResponse[RobotRead]:
    robots = await FleetService(session).list_robots(
        search=search,
        status=status_filter,
        zone_id=zone_id,
        battery_below=battery_below,
        fault_only=fault_only,
    )
    return ListResponse(items=[RobotRead.model_validate(robot) for robot in robots], total=len(robots))


@router.get("/robots/{robot_id}", response_model=RobotDetail)
async def get_robot(
    robot_id: str,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> RobotDetail:
    robot = await FleetService(session).get_robot(robot_id)
    return RobotDetail.model_validate(robot)


@router.post("/robots", response_model=RobotRead, status_code=status.HTTP_201_CREATED)
async def create_robot(
    payload: RobotCreate,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(require_roles(UserRole.ADMIN, UserRole.OPERATOR)),
) -> RobotRead:
    robot = await FleetService(session).create_robot(payload, actor)
    await session.commit()
    return RobotRead.model_validate(robot)


@router.patch("/robots/{robot_id}", response_model=RobotRead)
async def update_robot(
    robot_id: str,
    payload: RobotUpdate,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(require_roles(UserRole.ADMIN, UserRole.OPERATOR)),
) -> RobotRead:
    robot = await FleetService(session).update_robot(robot_id, payload, actor)
    await session.commit()
    return RobotRead.model_validate(robot)


@router.delete("/robots/{robot_id}", response_model=MessageResponse)
async def delete_robot(
    robot_id: str,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(require_roles(UserRole.ADMIN)),
) -> MessageResponse:
    await FleetService(session).delete_robot(robot_id, actor)
    await session.commit()
    return MessageResponse(message="Robot removed")
