from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.models.alert import Alert
from app.models.configuration import PlatformConfig
from app.models.enums import (
    AlertSeverity,
    AlertStatus,
    AlertType,
    ConnectivityState,
    MissionStatus,
    OperatingMode,
    RobotStatus,
    WeatherState,
)
from app.models.mission import Mission
from app.models.mission_event import MissionEvent
from app.models.robot import Robot
from app.models.telemetry import TelemetrySnapshot
from app.models.zone import Zone
from app.services.serializers import serialize_alert, serialize_robot
from app.simulator.state_machine import advance_progress, approach, coverage_route, point_on_route, route_length, should_emit
from app.ws.manager import WebSocketManager


logger = logging.getLogger(__name__)


class SimulatorCoordinator:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession], websocket_manager: WebSocketManager) -> None:
        self.session_factory = session_factory
        self.websocket_manager = websocket_manager
        self.task: asyncio.Task | None = None
        self.tick = 0
        self.runtime: dict[str, dict] = defaultdict(dict)
        self._running = False

    async def start(self) -> None:
        if self.task and not self.task.done():
            return
        self._running = True
        self.task = asyncio.create_task(self._loop(), name="roboyard-simulator")

    async def stop(self) -> None:
        self._running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

    async def _loop(self) -> None:
        settings = get_settings()
        while self._running:
            try:
                async with self.session_factory() as session:
                    await self._process_tick(session)
                    await session.commit()
            except Exception:  # noqa: BLE001
                logger.exception("simulator_tick_failed")
            await asyncio.sleep(settings.simulator_tick_seconds)

    async def _process_tick(self, session: AsyncSession) -> None:
        self.tick += 1
        config = await session.scalar(select(PlatformConfig).where(PlatformConfig.name == "default"))
        if not config:
            return
        self._advance_weather(config)

        zones = await session.execute(select(Zone))
        zones_by_id = {zone.id: zone for zone in zones.scalars().all()}
        missions_result = await session.execute(
            select(Mission).options(selectinload(Mission.robot), selectinload(Mission.zone)).order_by(Mission.created_at.desc())
        )
        missions = missions_result.scalars().all()
        active_by_robot = {}
        for mission in missions:
            if mission.status in {MissionStatus.ACTIVE, MissionStatus.PAUSED, MissionStatus.RETURNING_HOME, MissionStatus.SCHEDULED} and mission.robot_id not in active_by_robot:
                active_by_robot[mission.robot_id] = mission

        robots_result = await session.execute(select(Robot).options(selectinload(Robot.zone)).order_by(Robot.name.asc()))
        robots = robots_result.scalars().all()
        open_alerts: list[Alert] = []
        now = datetime.now(timezone.utc)
        for robot in robots:
            zone = zones_by_id[robot.zone_id]
            mission = active_by_robot.get(robot.id)
            runtime = self.runtime[robot.id]
            if mission and not mission.route_points:
                mission.route_points = coverage_route(zone.boundary, zone.charging_station)
            await self._advance_robot(session, robot, zone, mission, config, runtime, now, open_alerts)
            if self.tick % get_settings().telemetry_flush_interval == 0:
                await self._snapshot(session, robot, mission, config.current_weather)

        await self.websocket_manager.broadcast_json(
            {
                "type": "fleet_tick",
                "timestamp": now.isoformat(),
                "weather": {"state": config.current_weather.value, "intensity": round(config.weather_intensity, 2)},
                "robots": [serialize_robot(robot, active_by_robot.get(robot.id)) for robot in robots],
                "alerts": [serialize_alert(alert) for alert in open_alerts[-4:]],
            }
        )

    def _advance_weather(self, config: PlatformConfig) -> None:
        sequence = [
            (WeatherState.CLEAR, 0.08),
            (WeatherState.DRIZZLE, 0.18),
            (WeatherState.WIND_GUST, 0.22),
            (WeatherState.CLEAR, 0.1),
            (WeatherState.RAIN, 0.32),
        ]
        if self.tick % 16 == 0:
            index = (self.tick // 16) % len(sequence)
            state, intensity = sequence[index]
            config.current_weather = state
            config.weather_intensity = intensity

    async def _advance_robot(
        self,
        session: AsyncSession,
        robot: Robot,
        zone: Zone,
        mission: Mission | None,
        config: PlatformConfig,
        runtime: dict,
        now: datetime,
        open_alerts: list[Alert],
    ) -> None:
        runtime.setdefault("cooldowns", {})
        robot.last_seen_at = now

        if mission and mission.status == MissionStatus.SCHEDULED and mission.scheduled_start and mission.scheduled_start <= now:
            mission.status = MissionStatus.ACTIVE
            mission.started_at = now
            robot.status = RobotStatus.OPERATING
            robot.status_reason = f"Started scheduled mission {mission.name}"
            await self._event(session, robot, mission, "mission", "mission_started", f"{mission.name} started")

        if robot.status == RobotStatus.CHARGING:
            robot.battery_level = min(100.0, robot.battery_level + 3.6)
            robot.speed_mps = 0.0
            robot.tool_state = "standby"
            if robot.battery_level >= 98 and (not mission or mission.status == MissionStatus.COMPLETED):
                robot.status = RobotStatus.IDLE
                robot.status_reason = "Ready for next mission window"
            return

        if robot.status == RobotStatus.FAULT and runtime.get("fault_until", 0) <= self.tick:
            robot.status = RobotStatus.PAUSED
            robot.operating_mode = OperatingMode.AUTONOMOUS
            robot.status_reason = "Awaiting operator resume after fault"
            return

        if robot.status == RobotStatus.PAUSED and runtime.get("pause_until", 0) > self.tick:
            robot.speed_mps = 0.0
            return

        if robot.status == RobotStatus.WEATHER_PAUSED:
            robot.speed_mps = 0.0
            if config.current_weather in {WeatherState.CLEAR, WeatherState.DRIZZLE} and runtime.get("weather_until", 0) <= self.tick:
                robot.status = RobotStatus.OPERATING
                robot.status_reason = "Weather pause cleared"
                if mission and mission.status != MissionStatus.ABORTED:
                    mission.status = MissionStatus.ACTIVE
            return

        if robot.status == RobotStatus.MANUAL_OVERRIDE:
            robot.speed_mps = 0.0
            return

        if robot.status == RobotStatus.RETURNING_HOME:
            point, heading = approach(
                {"x": robot.position_x, "y": robot.position_y},
                zone.charging_station,
                max(robot.speed_mps, 1.2) * config.simulator_tick_seconds,
            )
            robot.position_x = point["x"]
            robot.position_y = point["y"]
            robot.heading_deg = heading
            robot.speed_mps = 1.2
            robot.battery_level = max(6.0, robot.battery_level - 0.18)
            if point == zone.charging_station:
                robot.status = RobotStatus.CHARGING
                robot.speed_mps = 0.0
                robot.charging_cycles += 1
                robot.status_reason = "Docked at charging station"
                if mission and mission.status != MissionStatus.ABORTED:
                    mission.status = MissionStatus.COMPLETED
                    mission.completed_at = now
                await self._event(session, robot, mission, "robot", "charging_started", "Robot docked for charging")
            return

        if not mission or mission.status in {MissionStatus.COMPLETED, MissionStatus.ABORTED}:
            robot.speed_mps = 0.0
            if robot.battery_level < 82:
                robot.status = RobotStatus.CHARGING
                robot.status_reason = "Topping up battery in idle window"
            else:
                robot.status = RobotStatus.IDLE
                robot.status_reason = "Monitoring for next mission"
            return

        if mission.status in {MissionStatus.PAUSED, MissionStatus.RETURNING_HOME} and robot.status != RobotStatus.RETURNING_HOME:
            robot.status = RobotStatus.PAUSED if mission.status == MissionStatus.PAUSED else RobotStatus.RETURNING_HOME
            robot.speed_mps = 0.0
            return

        route = mission.route_points
        total = route_length(route)
        speed = 1.25 + (robot.deterministic_seed % 4) * 0.14
        mission.progress_pct = advance_progress(mission.progress_pct, speed, config.simulator_tick_seconds, total)
        mission.completed_area_sqm = mission.target_area_sqm * (mission.progress_pct / 100.0)
        point, heading = point_on_route(route, mission.progress_pct)
        robot.position_x = point["x"]
        robot.position_y = point["y"]
        robot.heading_deg = heading
        robot.speed_mps = speed
        robot.status = RobotStatus.OPERATING
        robot.operating_mode = OperatingMode.AUTONOMOUS
        robot.tool_state = "cutting" if robot.robot_type.value == "lawn_mower" else "inspection"
        robot.status_reason = f"Executing {mission.name}"
        robot.total_runtime_minutes += config.simulator_tick_seconds / 60.0
        robot.total_distance_m += robot.speed_mps * config.simulator_tick_seconds
        robot.battery_level = max(5.0, robot.battery_level - (0.16 if robot.robot_type.value == "inspection" else 0.24))

        if self._emit_allowed(runtime, AlertType.WEATHER_SAFETY, 10) and config.current_weather in {WeatherState.RAIN, WeatherState.STORM}:
            robot.status = RobotStatus.WEATHER_PAUSED
            mission.status = MissionStatus.PAUSED
            robot.speed_mps = 0.0
            runtime["weather_until"] = self.tick + 3
            alert = await self._alert(
                session,
                robot,
                mission,
                zone,
                AlertType.WEATHER_SAFETY,
                AlertSeverity.CRITICAL,
                "Weather pause engaged",
                "Safety interlock paused the robot due to rain or wind risk.",
                {"weather": config.current_weather.value},
            )
            open_alerts.append(alert)
            return

        if self._emit_allowed(runtime, AlertType.OBSTACLE_DETECTED, 22) and should_emit(robot.deterministic_seed, self.tick, 22, 5):
            robot.status = RobotStatus.PAUSED
            robot.speed_mps = 0.0
            mission.status = MissionStatus.PAUSED
            runtime["pause_until"] = self.tick + 2
            alert = await self._alert(
                session,
                robot,
                mission,
                zone,
                AlertType.OBSTACLE_DETECTED,
                AlertSeverity.WARNING,
                "Obstacle detected in path",
                "Lidar hazard map shows an obstacle inside the active route corridor.",
                {"route_progress": f"{mission.progress_pct:.1f}"},
            )
            open_alerts.append(alert)
            return

        if self._emit_allowed(runtime, AlertType.LOST_CONNECTIVITY, 31) and should_emit(robot.deterministic_seed, self.tick, 31, 9):
            robot.connectivity_state = ConnectivityState.DEGRADED
            robot.signal_strength = max(32.0, robot.signal_strength - 28.0)
            alert = await self._alert(
                session,
                robot,
                mission,
                zone,
                AlertType.LOST_CONNECTIVITY,
                AlertSeverity.WARNING,
                "Connectivity degraded",
                "Robot mesh connectivity dipped below the operational threshold.",
                {"signal_strength": f"{robot.signal_strength:.1f}"},
            )
            open_alerts.append(alert)
        else:
            robot.connectivity_state = ConnectivityState.ONLINE
            robot.signal_strength = min(100.0, robot.signal_strength + 4.0)

        if self._emit_allowed(runtime, AlertType.COLLISION_RISK, 47) and should_emit(robot.deterministic_seed, self.tick, 47, 13):
            robot.status = RobotStatus.FAULT
            robot.speed_mps = 0.0
            mission.status = MissionStatus.PAUSED
            runtime["fault_until"] = self.tick + 3
            alert = await self._alert(
                session,
                robot,
                mission,
                zone,
                AlertType.COLLISION_RISK,
                AlertSeverity.CRITICAL,
                "Collision risk hold",
                "Proximity confidence crossed the collision risk threshold; hold inserted.",
                {"threshold": f"{config.collision_threshold:.2f}"},
            )
            open_alerts.append(alert)
            return

        if self._emit_allowed(runtime, AlertType.GEOFENCE_BREACH, 59) and should_emit(robot.deterministic_seed, self.tick, 59, 17):
            robot.status = RobotStatus.RETURNING_HOME
            mission.status = MissionStatus.RETURNING_HOME
            alert = await self._alert(
                session,
                robot,
                mission,
                zone,
                AlertType.GEOFENCE_BREACH,
                AlertSeverity.CRITICAL,
                "Geofence deviation detected",
                "Robot deviated beyond the permitted fence tolerance and is returning home.",
                {"tolerance_m": f"{config.geofence_tolerance_m:.1f}"},
            )
            open_alerts.append(alert)
            return

        if not runtime.get("low_battery_notified") and robot.battery_level <= config.low_battery_threshold:
            runtime["low_battery_notified"] = True
            robot.status = RobotStatus.RETURNING_HOME
            mission.status = MissionStatus.RETURNING_HOME
            alert = await self._alert(
                session,
                robot,
                mission,
                zone,
                AlertType.LOW_BATTERY,
                AlertSeverity.WARNING,
                "Low battery return initiated",
                "Battery crossed the return threshold and the robot is heading to charge.",
                {"battery": f"{robot.battery_level:.1f}"},
            )
            open_alerts.append(alert)
            return

        if mission.progress_pct >= 100.0:
            robot.status = RobotStatus.RETURNING_HOME
            mission.status = MissionStatus.RETURNING_HOME
            await self._event(session, robot, mission, "mission", "mission_completed", f"{mission.name} completed route coverage")

    def _emit_allowed(self, runtime: dict, alert_type: AlertType, cooldown: int) -> bool:
        last = runtime["cooldowns"].get(alert_type.value, -999)
        if self.tick - last >= cooldown:
            runtime["cooldowns"][alert_type.value] = self.tick
            return True
        return False

    async def _event(self, session: AsyncSession, robot: Robot, mission: Mission | None, category: str, event_type: str, message: str) -> None:
        session.add(
            MissionEvent(
                robot_id=robot.id,
                mission_id=mission.id if mission else None,
                category=category,
                event_type=event_type,
                message=message,
                payload={"robot_name": robot.name},
            )
        )

    async def _alert(
        self,
        session: AsyncSession,
        robot: Robot,
        mission: Mission | None,
        zone: Zone,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        metadata: dict,
    ) -> Alert:
        alert = Alert(
            robot_id=robot.id,
            mission_id=mission.id if mission else None,
            zone_id=zone.id,
            type=alert_type,
            severity=severity,
            status=AlertStatus.OPEN,
            title=title,
            message=message,
            context=metadata,
        )
        session.add(alert)
        await session.flush()
        await session.refresh(alert, ["robot", "mission"])
        await self._event(session, robot, mission, "alert", alert_type.value, title)
        return alert

    async def _snapshot(self, session: AsyncSession, robot: Robot, mission: Mission | None, weather: WeatherState) -> None:
        session.add(
            TelemetrySnapshot(
                robot_id=robot.id,
                mission_id=mission.id if mission else None,
                position_x=robot.position_x,
                position_y=robot.position_y,
                battery_level=robot.battery_level,
                speed_mps=robot.speed_mps,
                mission_progress_pct=mission.progress_pct if mission else 0.0,
                connectivity_state=robot.connectivity_state,
                robot_status=robot.status,
                operating_mode=robot.operating_mode,
                weather_state=weather,
                payload={"heading_deg": robot.heading_deg},
            )
        )
