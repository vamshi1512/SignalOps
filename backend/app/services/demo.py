from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.alert import Alert
from app.models.enums import (
    AlertSeverity,
    AlertStatus,
    AlertType,
    ConnectivityState,
    MissionStatus,
    MissionType,
    OperatingMode,
    RobotStatus,
    RobotType,
    UserRole,
    WeatherState,
)
from app.models.mission import Mission
from app.models.mission_event import MissionEvent
from app.models.robot import Robot
from app.models.telemetry import TelemetrySnapshot
from app.models.user import User
from app.models.zone import Zone
from app.repositories.users import UserRepository
from app.services.audit import AuditService
from app.services.configuration import ConfigurationService
from app.simulator.state_machine import coverage_route, point_on_route


DEMO_ACCOUNTS = [
    ("admin@roboyard.dev", "Avery Stone", "Mission lead", "Admin123!", UserRole.ADMIN),
    ("ops@roboyard.dev", "Noah Vega", "Fleet operator", "Ops123!", UserRole.OPERATOR),
    ("viewer@roboyard.dev", "Mila Hart", "Operations analyst", "Viewer123!", UserRole.VIEWER),
]

ZONE_DEFINITIONS = [
    {
        "name": "North Course",
        "slug": "north-course",
        "description": "Large primary grass sector used for mowing, fairway finishing, and perimeter inspection.",
        "color": "#22c55e",
        "boundary": [{"x": 24, "y": 24}, {"x": 420, "y": 24}, {"x": 420, "y": 220}, {"x": 24, "y": 220}],
        "charging_station": {"x": 40, "y": 40},
        "task_areas": [
            {"label": "Fairway A", "x": 72, "y": 58, "width": 134, "height": 92},
            {"label": "Fairway B", "x": 224, "y": 58, "width": 138, "height": 94},
        ],
        "weather_exposure": 1.0,
    },
    {
        "name": "Service Yard",
        "slug": "service-yard",
        "description": "Utility yard with narrow trailer lanes, pallet stacks, and elevated obstacle density.",
        "color": "#38bdf8",
        "boundary": [{"x": 450, "y": 30}, {"x": 780, "y": 30}, {"x": 780, "y": 240}, {"x": 450, "y": 240}],
        "charging_station": {"x": 470, "y": 50},
        "task_areas": [
            {"label": "Trailer Lane", "x": 520, "y": 84, "width": 116, "height": 68},
            {"label": "Supply Drop", "x": 652, "y": 150, "width": 92, "height": 54},
        ],
        "weather_exposure": 0.8,
    },
    {
        "name": "South Perimeter",
        "slug": "south-perimeter",
        "description": "Fence-line patrol strip for inspection bots and perimeter safety checks.",
        "color": "#f59e0b",
        "boundary": [{"x": 60, "y": 260}, {"x": 780, "y": 260}, {"x": 780, "y": 450}, {"x": 60, "y": 450}],
        "charging_station": {"x": 88, "y": 280},
        "task_areas": [
            {"label": "Fence Patrol", "x": 138, "y": 304, "width": 182, "height": 48},
            {"label": "Drainage Check", "x": 560, "y": 344, "width": 118, "height": 56},
        ],
        "weather_exposure": 1.2,
    },
    {
        "name": "East Orchard",
        "slug": "east-orchard",
        "description": "Mixed terrain orchard rows used for mowing passes and equipment transport demos.",
        "color": "#a78bfa",
        "boundary": [{"x": 438, "y": 262}, {"x": 780, "y": 262}, {"x": 780, "y": 450}, {"x": 438, "y": 450}],
        "charging_station": {"x": 462, "y": 282},
        "task_areas": [
            {"label": "Row 12", "x": 500, "y": 300, "width": 102, "height": 44},
            {"label": "Irrigation Loop", "x": 622, "y": 360, "width": 112, "height": 46},
        ],
        "weather_exposure": 1.1,
    },
]

ROBOT_DEFINITIONS = [
    ("RY-MOW-01", "Atlas Trim 900", RobotType.LAWN_MOWER, "MOW-900-A1", "v3.4.1", "north-course", 11),
    ("RY-MOW-02", "Atlas Trim 950", RobotType.LAWN_MOWER, "MOW-950-A2", "v3.4.3", "north-course", 17),
    ("RY-UTIL-03", "Cargo Mule X", RobotType.UTILITY, "UTIL-X3", "v2.8.9", "service-yard", 23),
    ("RY-INSP-04", "Perimeter Scout", RobotType.INSPECTION, "INSP-S4", "v5.1.2", "south-perimeter", 29),
    ("RY-UTIL-05", "Cargo Mule Mini", RobotType.UTILITY, "UTIL-M5", "v2.9.0", "service-yard", 31),
    ("RY-INSP-06", "Fence Watch", RobotType.INSPECTION, "INSP-F6", "v5.2.0", "south-perimeter", 37),
    ("RY-MOW-07", "Orchard Glide", RobotType.LAWN_MOWER, "MOW-O7", "v3.5.0", "east-orchard", 41),
    ("RY-UTIL-08", "Cargo Mule Field", RobotType.UTILITY, "UTIL-F8", "v3.0.1", "east-orchard", 47),
]


class DemoService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def seed(self) -> None:
        if await self.users.get_by_email("admin@roboyard.dev"):
            return

        config = await ConfigurationService(self.session).get_or_create()
        config.current_weather = WeatherState.DRIZZLE
        config.weather_intensity = 0.18

        seeded_users: dict[str, User] = {}
        for email, name, title, password, role in DEMO_ACCOUNTS:
            user = User(
                email=email,
                full_name=name,
                title=title,
                password_hash=hash_password(password),
                role=role,
                settings={
                    "density": "compact" if role == UserRole.ADMIN else "comfortable",
                    "alerts": True,
                    "telemetry_units": "metric",
                },
            )
            await self.users.add(user)
            seeded_users[email] = user

        zones: dict[str, Zone] = {}
        for definition in ZONE_DEFINITIONS:
            zone = Zone(**definition)
            self.session.add(zone)
            await self.session.flush()
            zones[zone.slug] = zone

        robots: list[Robot] = []
        zone_slug_by_serial = {serial: zone_slug for _, _, _, serial, _, zone_slug, _ in ROBOT_DEFINITIONS}
        for name, model, robot_type, serial, firmware_version, zone_slug, seed in ROBOT_DEFINITIONS:
            zone = zones[zone_slug]
            robot = Robot(
                name=name,
                slug=name.lower(),
                robot_type=robot_type,
                model=model,
                serial=serial,
                firmware_version=firmware_version,
                zone_id=zone.id,
                position_x=zone.charging_station["x"],
                position_y=zone.charging_station["y"],
                battery_level=max(36.0, 96.0 - (seed % 24)),
                deterministic_seed=seed,
                status=RobotStatus.IDLE,
                operating_mode=OperatingMode.AUTONOMOUS,
                connectivity_state=ConnectivityState.ONLINE,
                signal_strength=min(100.0, 86.0 + (seed % 14)),
                tool_state="standby",
                status_reason="Commissioned into seeded demo fleet",
                total_runtime_minutes=620 + seed * 7,
                total_distance_m=11_200 + seed * 138,
                charging_cycles=8 + (seed % 10),
                health_score=min(99.0, 89.0 + (seed % 10)),
            )
            self.session.add(robot)
            await self.session.flush()
            robots.append(robot)

        now = datetime.now(timezone.utc)
        for index, robot in enumerate(robots):
            zone = zones[zone_slug_by_serial[robot.serial]]
            route = coverage_route(zone.boundary, zone.charging_station)

            for history_offset in range(3, 0, -1):
                started = now - timedelta(hours=7 * history_offset + index)
                mission = Mission(
                    robot_id=robot.id,
                    zone_id=zone.id,
                    name=f"{zone.name} {self._historical_label(robot.robot_type)} {history_offset}",
                    mission_type=self._historical_mission_type(robot.robot_type),
                    status=MissionStatus.COMPLETED,
                    scheduled_start=started,
                    scheduled_end=started + timedelta(minutes=72),
                    started_at=started,
                    completed_at=started + timedelta(minutes=49 + index * 2 + history_offset),
                    estimated_duration_minutes=56 + index,
                    progress_pct=100.0,
                    target_area_sqm=760 + index * 58,
                    completed_area_sqm=740 + index * 53,
                    route_points=route,
                    replay_seed=robot.deterministic_seed,
                    operator_notes=f"Historical {self._historical_label(robot.robot_type).lower()} mission seeded for replay.",
                )
                self.session.add(mission)
                await self.session.flush()
                await self._seed_mission_track(
                    robot,
                    mission,
                    route,
                    started,
                    WeatherState.CLEAR if history_offset > 1 else WeatherState.DRIZZLE,
                )

            mission_type = self._live_mission_type(robot.robot_type)
            progress = min(82.0, 18.0 + index * 8.0)
            active = Mission(
                robot_id=robot.id,
                zone_id=zone.id,
                name=f"{zone.name} {self._live_label(robot.robot_type)}",
                mission_type=mission_type,
                status=MissionStatus.ACTIVE,
                scheduled_start=now - timedelta(minutes=14 + index),
                scheduled_end=now + timedelta(minutes=52 + index * 3),
                started_at=now - timedelta(minutes=12 + index),
                estimated_duration_minutes=58.0 + index,
                progress_pct=progress,
                target_area_sqm=840 + index * 48,
                completed_area_sqm=(840 + index * 48) * (progress / 100.0),
                route_points=route,
                replay_seed=robot.deterministic_seed,
                operator_notes="Live seeded mission for dashboard walkthroughs.",
            )
            self.session.add(active)
            await self.session.flush()

            if index < 4:
                point, heading = point_on_route(route, progress)
                robot.position_x = point["x"]
                robot.position_y = point["y"]
                robot.heading_deg = heading
                robot.speed_mps = 1.1 + (index * 0.18)
                robot.status = RobotStatus.OPERATING
                robot.tool_state = "cutting" if robot.robot_type == RobotType.LAWN_MOWER else "inspection"
                robot.status_reason = f"Executing {active.name}"
                if index == 2:
                    robot.connectivity_state = ConnectivityState.DEGRADED
                    robot.signal_strength = 58.0
                await self._seed_live_snapshot(robot, active, WeatherState.DRIZZLE, now)
            elif index == 4:
                active.status = MissionStatus.SCHEDULED
                active.scheduled_start = now + timedelta(minutes=18)
                active.started_at = None
                active.progress_pct = 0.0
                active.completed_area_sqm = 0.0
                robot.status = RobotStatus.CHARGING
                robot.battery_level = 42.0
                robot.speed_mps = 0.0
                robot.tool_state = "standby"
                robot.status_reason = "Charging before utility dispatch window"
            elif index == 5:
                point, heading = point_on_route(route, 36.0)
                active.progress_pct = 36.0
                active.completed_area_sqm = active.target_area_sqm * 0.36
                robot.position_x = point["x"]
                robot.position_y = point["y"]
                robot.heading_deg = heading
                robot.status = RobotStatus.MANUAL_OVERRIDE
                robot.operating_mode = OperatingMode.MANUAL
                robot.speed_mps = 0.0
                robot.tool_state = "standby"
                robot.status_reason = "Manual override active for fence-line verification"
                await self._seed_live_snapshot(robot, active, WeatherState.DRIZZLE, now)
                self.session.add(
                    MissionEvent(
                        robot_id=robot.id,
                        mission_id=active.id,
                        occurred_at=now - timedelta(minutes=2),
                        category="command",
                        event_type="manual_override",
                        message=f"{robot.name} switched to manual override during patrol verification",
                        payload={"robot_name": robot.name},
                    )
                )
            elif index == 6:
                active.status = MissionStatus.SCHEDULED
                active.scheduled_start = now + timedelta(minutes=34)
                active.started_at = None
                active.progress_pct = 0.0
                active.completed_area_sqm = 0.0
                robot.status = RobotStatus.IDLE
                robot.speed_mps = 0.0
                robot.tool_state = "standby"
                robot.status_reason = "Queued for orchard afternoon sweep"
            else:
                point, heading = point_on_route(route, 28.0)
                active.status = MissionStatus.PAUSED
                active.progress_pct = 28.0
                active.completed_area_sqm = active.target_area_sqm * 0.28
                robot.position_x = point["x"]
                robot.position_y = point["y"]
                robot.heading_deg = heading
                robot.status = RobotStatus.PAUSED
                robot.speed_mps = 0.0
                robot.tool_state = "standby"
                robot.status_reason = "Paused pending obstacle clearance in orchard row"
                await self._seed_live_snapshot(robot, active, WeatherState.DRIZZLE, now)

        await self._seed_alerts(robots, seeded_users, now)
        await self._seed_audit_entries(seeded_users, robots, now)

    def _historical_label(self, robot_type: RobotType) -> str:
        return {
            RobotType.LAWN_MOWER: "Coverage Sweep",
            RobotType.UTILITY: "Payload Run",
            RobotType.INSPECTION: "Fence Patrol",
        }[robot_type]

    def _historical_mission_type(self, robot_type: RobotType) -> MissionType:
        return {
            RobotType.LAWN_MOWER: MissionType.MOW,
            RobotType.UTILITY: MissionType.HAUL,
            RobotType.INSPECTION: MissionType.INSPECT,
        }[robot_type]

    def _live_label(self, robot_type: RobotType) -> str:
        return {
            RobotType.LAWN_MOWER: "Live Pass",
            RobotType.UTILITY: "Utility Run",
            RobotType.INSPECTION: "Patrol Loop",
        }[robot_type]

    def _live_mission_type(self, robot_type: RobotType) -> MissionType:
        return {
            RobotType.LAWN_MOWER: MissionType.MOW,
            RobotType.UTILITY: MissionType.HAUL,
            RobotType.INSPECTION: MissionType.PATROL,
        }[robot_type]

    async def _seed_mission_track(
        self,
        robot: Robot,
        mission: Mission,
        route: list[dict[str, float]],
        started_at: datetime,
        weather: WeatherState,
    ) -> None:
        for step in range(6):
            progress = step * 20
            point, heading = point_on_route(route, progress)
            self.session.add(
                TelemetrySnapshot(
                    robot_id=robot.id,
                    mission_id=mission.id,
                    recorded_at=started_at + timedelta(minutes=step * 8),
                    position_x=point["x"],
                    position_y=point["y"],
                    battery_level=max(18.0, 100.0 - step * 11.5),
                    speed_mps=1.1 + (robot.deterministic_seed % 4) * 0.1,
                    mission_progress_pct=progress,
                    connectivity_state=ConnectivityState.ONLINE,
                    robot_status=RobotStatus.OPERATING if progress < 100 else RobotStatus.RETURNING_HOME,
                    operating_mode=OperatingMode.AUTONOMOUS,
                    weather_state=weather,
                    payload={"heading_deg": heading},
                )
            )
            if step == 2:
                self.session.add(
                    MissionEvent(
                        robot_id=robot.id,
                        mission_id=mission.id,
                        occurred_at=started_at + timedelta(minutes=step * 8),
                        category="mission",
                        event_type="coverage_checkpoint",
                        message=f"{mission.name} crossed the midpoint coverage checkpoint",
                        payload={"robot_name": robot.name},
                    )
                )

        self.session.add(
            MissionEvent(
                robot_id=robot.id,
                mission_id=mission.id,
                occurred_at=started_at + timedelta(minutes=44),
                category="mission",
                event_type="mission_completed",
                message=f"{mission.name} completed successfully",
                payload={"robot_name": robot.name},
            )
        )

    async def _seed_live_snapshot(self, robot: Robot, mission: Mission, weather: WeatherState, now: datetime) -> None:
        previous_progress = max(0.0, mission.progress_pct - 5.0)
        previous_point, previous_heading = point_on_route(mission.route_points, previous_progress)
        self.session.add_all(
            [
                TelemetrySnapshot(
                    robot_id=robot.id,
                    mission_id=mission.id,
                    recorded_at=now - timedelta(minutes=3),
                    position_x=previous_point["x"],
                    position_y=previous_point["y"],
                    battery_level=min(100.0, robot.battery_level + 2.0),
                    speed_mps=max(robot.speed_mps, 0.8),
                    mission_progress_pct=previous_progress,
                    connectivity_state=robot.connectivity_state,
                    robot_status=RobotStatus.OPERATING if robot.status == RobotStatus.MANUAL_OVERRIDE else robot.status,
                    operating_mode=OperatingMode.AUTONOMOUS if robot.status == RobotStatus.MANUAL_OVERRIDE else robot.operating_mode,
                    weather_state=weather,
                    payload={"heading_deg": previous_heading},
                ),
                TelemetrySnapshot(
                    robot_id=robot.id,
                    mission_id=mission.id,
                    recorded_at=now,
                    position_x=robot.position_x,
                    position_y=robot.position_y,
                    battery_level=robot.battery_level,
                    speed_mps=robot.speed_mps,
                    mission_progress_pct=mission.progress_pct,
                    connectivity_state=robot.connectivity_state,
                    robot_status=robot.status,
                    operating_mode=robot.operating_mode,
                    weather_state=weather,
                    payload={"heading_deg": robot.heading_deg},
                ),
            ]
        )

    async def _seed_alerts(self, robots: list[Robot], users: dict[str, User], now: datetime) -> None:
        active_like = await self.session.execute(
            select(Mission).where(Mission.status.in_([MissionStatus.ACTIVE, MissionStatus.PAUSED, MissionStatus.SCHEDULED]))
        )
        mission_by_robot = {mission.robot_id: mission for mission in active_like.scalars().all()}
        if not robots:
            return

        admin = users["admin@roboyard.dev"]
        alerts = [
            Alert(
                robot_id=robots[0].id,
                mission_id=mission_by_robot[robots[0].id].id,
                zone_id=robots[0].zone_id,
                type=AlertType.OBSTACLE_DETECTED,
                severity=AlertSeverity.WARNING,
                status=AlertStatus.OPEN,
                title="Obstacle cluster in mowing lane",
                message="Front lidar picked up an unplanned obstacle cluster near Fairway A.",
                context={"zone": "Fairway A", "distance_m": "2.4"},
                occurred_at=now - timedelta(minutes=4),
            ),
            Alert(
                robot_id=robots[2].id,
                mission_id=mission_by_robot[robots[2].id].id,
                zone_id=robots[2].zone_id,
                type=AlertType.LOST_CONNECTIVITY,
                severity=AlertSeverity.WARNING,
                status=AlertStatus.OPEN,
                title="Telemetry signal degraded",
                message="Mesh signal dropped below the degraded threshold for 12 seconds.",
                context={"rssi": "-85", "zone": "Trailer Lane"},
                occurred_at=now - timedelta(minutes=7),
            ),
            Alert(
                robot_id=robots[3].id,
                mission_id=mission_by_robot[robots[3].id].id,
                zone_id=robots[3].zone_id,
                type=AlertType.WEATHER_SAFETY,
                severity=AlertSeverity.CRITICAL,
                status=AlertStatus.ACKNOWLEDGED,
                title="Weather pause engaged",
                message="Rain safety lockout held the patrol robot at the south fence line.",
                notes="Holding until drizzle subsides below the pause threshold.",
                context={"rain_intensity": "0.18", "wind": "moderate"},
                acknowledged_by_id=admin.id,
                acknowledged_at=now - timedelta(minutes=3),
                occurred_at=now - timedelta(minutes=8),
            ),
            Alert(
                robot_id=robots[5].id,
                mission_id=mission_by_robot[robots[5].id].id,
                zone_id=robots[5].zone_id,
                type=AlertType.OPERATOR_OVERRIDE,
                severity=AlertSeverity.INFO,
                status=AlertStatus.OPEN,
                title="Manual override active",
                message="Operator took temporary control to verify a fence-line anomaly.",
                context={"operator": "Noah Vega"},
                occurred_at=now - timedelta(minutes=2),
            ),
            Alert(
                robot_id=robots[4].id,
                mission_id=mission_by_robot[robots[4].id].id,
                zone_id=robots[4].zone_id,
                type=AlertType.CHARGING_CYCLE,
                severity=AlertSeverity.INFO,
                status=AlertStatus.RESOLVED,
                title="Charging cycle completed",
                message="Utility robot completed a top-up cycle and is ready for the next window.",
                context={"dock": "Service Yard Bay 1"},
                resolved_at=now - timedelta(minutes=20),
                occurred_at=now - timedelta(minutes=36),
            ),
        ]
        self.session.add_all(alerts)

    async def _seed_audit_entries(self, users: dict[str, User], robots: list[Robot], now: datetime) -> None:
        operator = users["ops@roboyard.dev"]
        admin = users["admin@roboyard.dev"]
        audit = AuditService(self.session)
        await audit.log(
            actor=operator,
            action="mission.command.pause",
            resource_type="robot",
            resource_id=robots[0].id,
            message="Paused RY-MOW-01 after obstacle cluster alert",
            details={"timestamp": (now - timedelta(minutes=4)).isoformat()},
        )
        await audit.log(
            actor=operator,
            action="alert.acknowledge",
            resource_type="alert",
            resource_id="seed-alert-weather",
            message="Acknowledged weather safety lockout for south perimeter patrol",
            details={"robot": robots[3].name},
        )
        await audit.log(
            actor=admin,
            action="config.update",
            resource_type="platform_config",
            resource_id="default",
            message="Adjusted low battery threshold to 24% for demo profile",
            details={"low_battery_threshold": "24"},
        )
        await audit.log(
            actor=operator,
            action="mission.command.manual_override",
            resource_type="robot",
            resource_id=robots[5].id,
            message="Enabled manual override for fence-line verification",
            details={"zone": "South Perimeter"},
        )
