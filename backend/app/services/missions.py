from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import ApiError
from app.models.enums import MissionStatus, OperatingMode, RobotStatus
from app.models.mission import Mission
from app.models.mission_event import MissionEvent
from app.models.robot import Robot
from app.models.user import User
from app.models.zone import Zone
from app.schemas.missions import MissionCreate
from app.services.audit import AuditService
from app.services.serializers import serialize_mission
from app.simulator.state_machine import coverage_route


class MissionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_missions(self, *, status: MissionStatus | None = None, robot_id: str | None = None) -> list[dict]:
        query = select(Mission).options(selectinload(Mission.robot), selectinload(Mission.zone)).order_by(Mission.created_at.desc())
        if status:
            query = query.where(Mission.status == status)
        if robot_id:
            query = query.where(Mission.robot_id == robot_id)
        result = await self.session.execute(query)
        return [serialize_mission(mission) for mission in result.scalars().all()]

    async def get_mission(self, mission_id: str) -> Mission:
        result = await self.session.execute(
            select(Mission)
            .where(Mission.id == mission_id)
            .options(selectinload(Mission.robot), selectinload(Mission.zone))
        )
        mission = result.scalar_one_or_none()
        if not mission:
            raise ApiError("mission_not_found", "Mission not found", status_code=404)
        return mission

    async def create_mission(self, payload: MissionCreate, actor: User) -> dict:
        robot = await self.session.get(Robot, payload.robot_id, options=[selectinload(Robot.zone)])
        zone = await self.session.get(Zone, payload.zone_id)
        if not robot:
            raise ApiError("robot_not_found", "Robot not found", status_code=404)
        if not zone:
            raise ApiError("zone_not_found", "Zone not found", status_code=404)
        existing = await self.session.execute(
            select(Mission).where(
                Mission.robot_id == payload.robot_id,
                Mission.status.in_(
                    [
                        MissionStatus.SCHEDULED,
                        MissionStatus.ACTIVE,
                        MissionStatus.PAUSED,
                        MissionStatus.RETURNING_HOME,
                    ]
                ),
            )
        )
        if existing.scalar_one_or_none():
            raise ApiError("mission_conflict", "Robot already has an active or scheduled mission", status_code=409)
        route = coverage_route(zone.boundary, zone.charging_station)
        now = datetime.now(timezone.utc)
        is_scheduled = bool(payload.scheduled_start and payload.scheduled_start > now)
        mission = Mission(
            robot_id=robot.id,
            zone_id=zone.id,
            name=payload.name,
            mission_type=payload.mission_type,
            status=MissionStatus.SCHEDULED if is_scheduled else MissionStatus.ACTIVE,
            scheduled_start=payload.scheduled_start,
            scheduled_end=payload.scheduled_end,
            started_at=None if is_scheduled else now,
            estimated_duration_minutes=payload.estimated_duration_minutes,
            target_area_sqm=payload.target_area_sqm,
            route_points=route,
            replay_seed=robot.deterministic_seed,
            operator_notes=payload.operator_notes,
        )
        self.session.add(mission)
        await self.session.flush()
        robot.status = RobotStatus.OPERATING if mission.status == MissionStatus.ACTIVE else RobotStatus.IDLE
        robot.operating_mode = OperatingMode.AUTONOMOUS
        robot.status_reason = (
            f"Mission {mission.name} scheduled for dispatch"
            if is_scheduled
            else f"Mission {mission.name} dispatched"
        )
        self.session.add(
            MissionEvent(
                robot_id=robot.id,
                mission_id=mission.id,
                category="mission",
                event_type="mission_created",
                message=f"Mission {mission.name} created",
                payload={"status": mission.status.value},
            )
        )
        await AuditService(self.session).log(
            actor=actor,
            action="mission.create",
            resource_type="mission",
            resource_id=mission.id,
            message=f"Created mission {mission.name}",
            details={"robot_id": robot.id, "zone_id": zone.id},
        )
        await self.session.refresh(mission, ["robot", "zone"])
        return serialize_mission(mission)

    async def command_robot(self, robot_id: str, command: str, actor: User, note: str | None = None) -> dict:
        result = await self.session.execute(
            select(Robot)
            .where(Robot.id == robot_id)
            .options(selectinload(Robot.zone), selectinload(Robot.missions))
        )
        robot = result.scalar_one_or_none()
        if not robot:
            raise ApiError("robot_not_found", "Robot not found", status_code=404)

        mission = next(
            (item for item in robot.missions if item.status in {MissionStatus.ACTIVE, MissionStatus.PAUSED, MissionStatus.RETURNING_HOME, MissionStatus.SCHEDULED}),
            None,
        )
        if not mission:
            raise ApiError("mission_not_found", "No active or scheduled mission for robot", status_code=404)

        if command == "pause":
            mission.status = MissionStatus.PAUSED
            robot.status = RobotStatus.PAUSED
            robot.speed_mps = 0.0
            robot.status_reason = "Paused by operator"
        elif command == "resume":
            mission.status = MissionStatus.ACTIVE
            if robot.status not in {RobotStatus.MANUAL_OVERRIDE, RobotStatus.FAULT}:
                robot.status = RobotStatus.OPERATING
                robot.status_reason = "Mission resumed"
        elif command == "return_to_base":
            mission.status = MissionStatus.RETURNING_HOME
            robot.status = RobotStatus.RETURNING_HOME
            robot.status_reason = "Returning to charging station"
        elif command == "emergency_stop":
            mission.status = MissionStatus.ABORTED
            robot.status = RobotStatus.FAULT
            robot.operating_mode = OperatingMode.EMERGENCY_STOP
            robot.speed_mps = 0.0
            robot.status_reason = "Emergency stop engaged"
        elif command == "manual_override":
            robot.status = RobotStatus.MANUAL_OVERRIDE
            robot.operating_mode = OperatingMode.MANUAL
            robot.speed_mps = 0.0
            robot.status_reason = "Manual override active"
        elif command == "clear_override":
            robot.operating_mode = OperatingMode.AUTONOMOUS
            mission.status = MissionStatus.ACTIVE
            robot.status = RobotStatus.OPERATING
            robot.status_reason = "Autonomy restored"

        mission.command_queue = [
            *mission.command_queue,
            {
                "command": command,
                "by": actor.full_name,
                "note": note or "",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        ]
        self.session.add(
            MissionEvent(
                robot_id=robot.id,
                mission_id=mission.id,
                category="command",
                event_type=command,
                message=note or f"Operator issued {command}",
                payload={"actor": actor.email},
            )
        )
        await self.session.flush()
        await AuditService(self.session).log(
            actor=actor,
            action=f"mission.command.{command}",
            resource_type="mission",
            resource_id=mission.id,
            message=f"Issued {command} to {robot.name}",
            details={"robot_id": robot.id},
        )
        await self.session.refresh(mission, ["robot", "zone"])
        return serialize_mission(mission)
