from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import ApiError
from app.models.mission import Mission
from app.models.enums import MissionStatus, RobotStatus
from app.models.robot import Robot
from app.models.user import User
from app.models.zone import Zone
from app.schemas.fleet import RobotCreate, RobotUpdate
from app.services.audit import AuditService
from app.services.serializers import serialize_robot, serialize_zone


class FleetService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_zones(self) -> list[dict]:
        result = await self.session.execute(select(Zone).order_by(Zone.name.asc()))
        return [serialize_zone(zone) for zone in result.scalars().all()]

    async def _active_missions(self) -> dict[str, Mission]:
        result = await self.session.execute(
            select(Mission)
            .where(Mission.status.in_([MissionStatus.ACTIVE, MissionStatus.PAUSED, MissionStatus.RETURNING_HOME]))
            .options(selectinload(Mission.zone), selectinload(Mission.robot))
        )
        return {mission.robot_id: mission for mission in result.scalars().all()}

    async def list_robots(
        self,
        *,
        search: str | None = None,
        status: RobotStatus | None = None,
        zone_id: str | None = None,
        battery_below: float | None = None,
        fault_only: bool = False,
    ) -> list[dict]:
        filters = []
        if search:
            pattern = f"%{search.lower()}%"
            filters.append(or_(Robot.name.ilike(pattern), Robot.model.ilike(pattern), Robot.serial.ilike(pattern)))
        if status:
            filters.append(Robot.status == status)
        if zone_id:
            filters.append(Robot.zone_id == zone_id)
        if battery_below is not None:
            filters.append(Robot.battery_level <= battery_below)
        if fault_only:
            filters.append(Robot.status == RobotStatus.FAULT)

        query = select(Robot).options(selectinload(Robot.zone)).order_by(Robot.name.asc())
        if filters:
            query = query.where(*filters)
        result = await self.session.execute(query)
        active = await self._active_missions()
        return [serialize_robot(robot, active.get(robot.id)) for robot in result.scalars().all()]

    async def get_robot(self, robot_id: str) -> dict:
        result = await self.session.execute(
            select(Robot).where(Robot.id == robot_id).options(selectinload(Robot.zone), selectinload(Robot.missions))
        )
        robot = result.scalar_one_or_none()
        if not robot:
            raise ApiError("robot_not_found", "Robot not found", status_code=404)
        active = next(
            (mission for mission in robot.missions if mission.status in {MissionStatus.ACTIVE, MissionStatus.PAUSED, MissionStatus.RETURNING_HOME}),
            None,
        )
        return serialize_robot(robot, active)

    async def create_robot(self, payload: RobotCreate, actor: User) -> dict:
        zone = await self.session.get(Zone, payload.zone_id)
        if not zone:
            raise ApiError("zone_not_found", "Zone not found", status_code=404)
        slug = payload.name.lower().replace(" ", "-")
        existing = await self.session.execute(
            select(Robot).where((Robot.name == payload.name) | (Robot.serial == payload.serial) | (Robot.slug == slug))
        )
        if existing.scalar_one_or_none():
            raise ApiError("robot_already_exists", "Robot name or serial already exists", status_code=409)
        robot = Robot(
            name=payload.name,
            slug=slug,
            robot_type=payload.robot_type,
            model=payload.model,
            serial=payload.serial,
            firmware_version=payload.firmware_version,
            zone_id=payload.zone_id,
            battery_level=payload.battery_level,
            position_x=payload.position_x,
            position_y=payload.position_y,
            deterministic_seed=payload.deterministic_seed,
            status_reason="Provisioned and awaiting mission dispatch",
        )
        self.session.add(robot)
        await self.session.flush()
        await AuditService(self.session).log(
            actor=actor,
            action="robot.create",
            resource_type="robot",
            resource_id=robot.id,
            message=f"Created robot {robot.name}",
            details={"model": robot.model, "zone_id": robot.zone_id},
        )
        await self.session.refresh(robot, ["zone"])
        return serialize_robot(robot)

    async def update_robot(self, robot_id: str, payload: RobotUpdate, actor: User) -> dict:
        robot = await self.session.get(Robot, robot_id, options=[selectinload(Robot.zone)])
        if not robot:
            raise ApiError("robot_not_found", "Robot not found", status_code=404)
        updates = payload.model_dump(exclude_none=True)
        if "name" in updates:
            next_slug = str(updates["name"]).lower().replace(" ", "-")
            existing = await self.session.execute(select(Robot).where(Robot.slug == next_slug, Robot.id != robot_id))
            if existing.scalar_one_or_none():
                raise ApiError("robot_name_conflict", "Another robot already uses that name", status_code=409)
            updates["slug"] = next_slug
        if "zone_id" in updates:
            zone = await self.session.get(Zone, updates["zone_id"])
            if not zone:
                raise ApiError("zone_not_found", "Zone not found", status_code=404)
        for field, value in updates.items():
            setattr(robot, field, value)
        await self.session.flush()
        await AuditService(self.session).log(
            actor=actor,
            action="robot.update",
            resource_type="robot",
            resource_id=robot.id,
            message=f"Updated robot {robot.name}",
            details={key: str(value) for key, value in updates.items()},
        )
        await self.session.refresh(robot, ["zone"])
        return serialize_robot(robot)

    async def delete_robot(self, robot_id: str, actor: User) -> None:
        robot = await self.session.get(Robot, robot_id)
        if not robot:
            raise ApiError("robot_not_found", "Robot not found", status_code=404)
        await AuditService(self.session).log(
            actor=actor,
            action="robot.delete",
            resource_type="robot",
            resource_id=robot.id,
            message=f"Removed robot {robot.name}",
        )
        await self.session.delete(robot)
