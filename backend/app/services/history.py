from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import ApiError
from app.models.alert import Alert
from app.models.mission import Mission
from app.models.mission_event import MissionEvent
from app.models.robot import Robot
from app.models.telemetry import TelemetrySnapshot
from app.services.serializers import serialize_alert, serialize_event, serialize_mission, serialize_robot, serialize_telemetry


class HistoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def robot_history(self, robot_id: str) -> dict:
        result = await self.session.execute(
            select(Robot)
            .where(Robot.id == robot_id)
            .options(
                selectinload(Robot.zone),
                selectinload(Robot.missions).selectinload(Mission.zone),
                selectinload(Robot.missions).selectinload(Mission.robot),
            )
        )
        robot = result.scalar_one_or_none()
        if not robot:
            raise ApiError("robot_not_found", "Robot not found", status_code=404)

        telemetry = await self.session.execute(
            select(TelemetrySnapshot)
            .where(TelemetrySnapshot.robot_id == robot_id)
            .order_by(TelemetrySnapshot.recorded_at.desc())
            .limit(160)
        )
        events = await self.session.execute(
            select(MissionEvent)
            .where(MissionEvent.robot_id == robot_id)
            .order_by(MissionEvent.occurred_at.desc())
            .limit(80)
        )
        alerts = await self.session.execute(
            select(Alert)
            .where(Alert.robot_id == robot_id)
            .options(selectinload(Alert.robot), selectinload(Alert.mission))
            .order_by(Alert.occurred_at.desc())
            .limit(40)
        )
        return {
            "robot": serialize_robot(robot),
            "telemetry": [serialize_telemetry(item) for item in reversed(telemetry.scalars().all())],
            "events": [serialize_event(item) for item in events.scalars().all()],
            "missions": [serialize_mission(item) for item in sorted(robot.missions, key=lambda mission: mission.created_at, reverse=True)],
            "alerts": [serialize_alert(item) for item in alerts.scalars().all()],
        }

    async def mission_replay(self, mission_id: str) -> dict:
        result = await self.session.execute(
            select(Mission)
            .where(Mission.id == mission_id)
            .options(selectinload(Mission.robot), selectinload(Mission.zone))
        )
        mission = result.scalar_one_or_none()
        if not mission:
            raise ApiError("mission_not_found", "Mission not found", status_code=404)
        telemetry = await self.session.execute(
            select(TelemetrySnapshot)
            .where(TelemetrySnapshot.mission_id == mission_id)
            .order_by(TelemetrySnapshot.recorded_at.asc())
        )
        events = await self.session.execute(
            select(MissionEvent)
            .where(MissionEvent.mission_id == mission_id)
            .order_by(MissionEvent.occurred_at.asc())
        )
        return {
            "mission": serialize_mission(mission),
            "telemetry": [serialize_telemetry(item) for item in telemetry.scalars().all()],
            "events": [serialize_event(item) for item in events.scalars().all()],
        }
