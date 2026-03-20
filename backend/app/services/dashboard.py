from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.alert import Alert
from app.models.enums import AlertStatus, MissionStatus, RobotStatus
from app.models.mission import Mission
from app.models.mission_event import MissionEvent
from app.models.robot import Robot
from app.models.telemetry import TelemetrySnapshot
from app.models.zone import Zone
from app.services.configuration import ConfigurationService
from app.services.fleet import FleetService
from app.services.serializers import serialize_alert, serialize_mission, serialize_robot, serialize_zone


STATUS_COLORS = {
    RobotStatus.OPERATING: "#22c55e",
    RobotStatus.CHARGING: "#38bdf8",
    RobotStatus.PAUSED: "#f59e0b",
    RobotStatus.RETURNING_HOME: "#c084fc",
    RobotStatus.FAULT: "#fb7185",
    RobotStatus.MANUAL_OVERRIDE: "#f97316",
    RobotStatus.IDLE: "#64748b",
    RobotStatus.WEATHER_PAUSED: "#60a5fa",
}


class DashboardService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def overview(self) -> dict:
        config = await ConfigurationService(self.session).get_or_create()
        robots = await FleetService(self.session).list_robots()
        zones_result = await self.session.execute(select(Zone).order_by(Zone.name.asc()))
        zones = [serialize_zone(zone) for zone in zones_result.scalars().all()]
        alerts_result = await self.session.execute(
            select(Alert)
            .options(selectinload(Alert.robot), selectinload(Alert.mission))
            .order_by(Alert.occurred_at.desc())
        )
        alerts = alerts_result.scalars().all()
        active_alerts = [serialize_alert(alert) for alert in alerts if alert.status == AlertStatus.OPEN][:8]

        missions_result = await self.session.execute(
            select(Mission).options(selectinload(Mission.robot), selectinload(Mission.zone)).order_by(Mission.created_at.desc())
        )
        missions = missions_result.scalars().all()
        active_missions = [
            serialize_mission(mission)
            for mission in missions
            if mission.status in {MissionStatus.ACTIVE, MissionStatus.PAUSED, MissionStatus.RETURNING_HOME, MissionStatus.SCHEDULED}
        ][:8]

        telemetry_result = await self.session.execute(
            select(TelemetrySnapshot).order_by(TelemetrySnapshot.recorded_at.desc()).limit(400)
        )
        telemetry = list(reversed(telemetry_result.scalars().all()))
        event_result = await self.session.execute(select(MissionEvent).order_by(MissionEvent.occurred_at.desc()).limit(40))
        events = event_result.scalars().all()

        battery_trend = self._battery_trend(telemetry)
        utilization_trend = self._utilization_trend(telemetry)
        mission_area_trend = self._mission_area_trend(missions)
        alert_frequency_trend = self._alert_frequency_trend(alerts)
        metrics = self._metrics(
            robots,
            missions,
            alerts,
            utilization_trend=utilization_trend,
            mission_area_trend=mission_area_trend,
            alert_frequency_trend=alert_frequency_trend,
        )
        return {
            "generated_at": datetime.now(timezone.utc),
            "metrics": metrics,
            "fleet_status_distribution": self._status_distribution(robots),
            "battery_trend": battery_trend,
            "utilization_trend": utilization_trend,
            "mission_area_trend": mission_area_trend,
            "alert_frequency_trend": alert_frequency_trend,
            "downtime_by_robot": self._downtime_by_robot(robots, telemetry),
            "robots": robots,
            "zones": zones,
            "active_alerts": active_alerts,
            "active_missions": active_missions,
            "activity": self._activity(events, alerts),
            "weather": {
                "state": config.current_weather,
                "intensity": config.weather_intensity,
                "updated_at": config.updated_at,
            },
        }

    def _metrics(
        self,
        robots: list[dict],
        missions: list[Mission],
        alerts: list[Alert],
        *,
        utilization_trend: list[dict],
        mission_area_trend: list[dict],
        alert_frequency_trend: list[dict],
    ) -> list[dict]:
        active_robots = sum(1 for robot in robots if robot["status"] == RobotStatus.OPERATING)
        utilization = (active_robots / len(robots) * 100) if robots else 0
        completed_area = sum(mission.completed_area_sqm for mission in missions if mission.status == MissionStatus.COMPLETED)
        open_alerts = sum(1 for alert in alerts if alert.status == AlertStatus.OPEN)
        charging_cycles = sum(robot["charging_cycles"] for robot in robots)
        durations = [mission.estimated_duration_minutes for mission in missions if mission.completed_at]
        avg_duration = sum(durations) / len(durations) if durations else 0
        recent_avg_duration = sum(durations[:3]) / len(durations[:3]) if durations[:3] else avg_duration
        prior_avg_duration = sum(durations[3:6]) / len(durations[3:6]) if durations[3:6] else recent_avg_duration
        live_robot_delta = round((self._series_delta(utilization_trend) / 100.0) * len(robots), 1)
        return [
            {"label": "Live Robots", "value": active_robots, "delta": live_robot_delta, "suffix": ""},
            {"label": "Fleet Utilization", "value": round(utilization, 1), "delta": self._series_delta(utilization_trend), "suffix": "%"},
            {"label": "Completed Area", "value": round(completed_area, 1), "delta": self._series_delta(mission_area_trend), "suffix": " sqm"},
            {"label": "Open Alerts", "value": open_alerts, "delta": -self._series_delta(alert_frequency_trend), "suffix": ""},
            {"label": "Charging Cycles", "value": charging_cycles, "delta": sum(1 for robot in robots if robot["status"] == RobotStatus.CHARGING), "suffix": ""},
            {"label": "Avg Mission", "value": round(avg_duration, 1), "delta": round(recent_avg_duration - prior_avg_duration, 1), "suffix": " min"},
        ]

    def _series_delta(self, points: list[dict]) -> float:
        if len(points) < 2:
            return 0.0
        return round(points[-1]["value"] - points[-2]["value"], 1)

    def _status_distribution(self, robots: list[dict]) -> list[dict]:
        counts = Counter(robot["status"] for robot in robots)
        return [
            {"label": status.value, "value": count, "color": STATUS_COLORS.get(status, "#64748b")}
            for status, count in counts.items()
        ]

    def _battery_trend(self, telemetry: list[TelemetrySnapshot]) -> list[dict]:
        buckets: dict[str, list[float]] = defaultdict(list)
        for item in telemetry:
            buckets[item.recorded_at.strftime("%H:%M")].append(item.battery_level)
        points = list(buckets.items())[-8:]
        return [{"label": label, "value": round(sum(values) / len(values), 1)} for label, values in points]

    def _utilization_trend(self, telemetry: list[TelemetrySnapshot]) -> list[dict]:
        buckets: dict[str, list[int]] = defaultdict(list)
        for item in telemetry:
            buckets[item.recorded_at.strftime("%H:%M")].append(1 if item.robot_status == RobotStatus.OPERATING else 0)
        points = list(buckets.items())[-8:]
        return [{"label": label, "value": round(sum(values) / len(values) * 100, 1)} for label, values in points]

    def _mission_area_trend(self, missions: list[Mission]) -> list[dict]:
        since = datetime.now(timezone.utc) - timedelta(days=7)
        buckets: dict[str, float] = defaultdict(float)
        for mission in missions:
            created_at = mission.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            if created_at >= since:
                buckets[created_at.strftime("%a")] += mission.completed_area_sqm or mission.target_area_sqm
        return [{"label": label, "value": round(value, 1)} for label, value in list(buckets.items())[-7:]]

    def _alert_frequency_trend(self, alerts: list[Alert]) -> list[dict]:
        buckets: dict[str, int] = defaultdict(int)
        for alert in alerts:
            buckets[alert.occurred_at.strftime("%H:%M")] += 1
        return [{"label": label, "value": value} for label, value in list(buckets.items())[-8:]]

    def _downtime_by_robot(self, robots: list[dict], telemetry: list[TelemetrySnapshot]) -> list[dict]:
        by_robot: dict[str, list[int]] = defaultdict(list)
        for item in telemetry:
            by_robot[item.robot_id].append(0 if item.robot_status == RobotStatus.OPERATING else 1)
        points = []
        for robot in robots[:6]:
            values = by_robot.get(robot["id"], [1])
            points.append(
                {
                    "label": robot["name"],
                    "value": round(sum(values) / len(values) * 100, 1),
                    "color": "#f59e0b" if robot["status"] != RobotStatus.OPERATING else "#22c55e",
                }
            )
        return points

    def _activity(self, events: list[MissionEvent], alerts: list[Alert]) -> list[dict]:
        items = [
            {
                "id": event.id,
                "timestamp": event.occurred_at,
                "category": event.category,
                "title": event.event_type.replace("_", " "),
                "detail": event.message,
                "robot_name": event.payload.get("robot_name") if isinstance(event.payload, dict) else None,
            }
            for event in events[:8]
        ]
        items.extend(
            {
                "id": alert.id,
                "timestamp": alert.occurred_at,
                "category": "alert",
                "title": alert.title,
                "detail": alert.message,
                "robot_name": alert.robot.name if alert.robot else None,
            }
            for alert in alerts[:4]
        )
        items.sort(key=lambda item: item["timestamp"], reverse=True)
        return items[:10]
