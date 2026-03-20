from __future__ import annotations

from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class ZoneType(StrEnum):
    PRIMARY = "primary"
    TASK = "task"
    CHARGING = "charging"
    NO_GO = "no_go"


class RobotType(StrEnum):
    LAWN_MOWER = "lawn_mower"
    UTILITY = "utility"
    INSPECTION = "inspection"


class RobotStatus(StrEnum):
    IDLE = "idle"
    OPERATING = "operating"
    PAUSED = "paused"
    CHARGING = "charging"
    RETURNING_HOME = "returning_home"
    FAULT = "fault"
    MANUAL_OVERRIDE = "manual_override"
    WEATHER_PAUSED = "weather_paused"


class OperatingMode(StrEnum):
    AUTONOMOUS = "autonomous"
    MANUAL = "manual"
    EMERGENCY_STOP = "emergency_stop"


class ConnectivityState(StrEnum):
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"


class MissionType(StrEnum):
    MOW = "mow"
    INSPECT = "inspect"
    PATROL = "patrol"
    HAUL = "haul"


class MissionStatus(StrEnum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    RETURNING_HOME = "returning_home"
    COMPLETED = "completed"
    ABORTED = "aborted"


class AlertSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(StrEnum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class AlertType(StrEnum):
    LOW_BATTERY = "low_battery"
    STUCK_ROBOT = "stuck_robot"
    COLLISION_RISK = "collision_risk"
    OBSTACLE_DETECTED = "obstacle_detected"
    WEATHER_SAFETY = "weather_safety"
    LOST_CONNECTIVITY = "lost_connectivity"
    GEOFENCE_BREACH = "geofence_breach"
    OPERATOR_OVERRIDE = "operator_override"
    CHARGING_CYCLE = "charging_cycle"


class WeatherState(StrEnum):
    CLEAR = "clear"
    DRIZZLE = "drizzle"
    RAIN = "rain"
    WIND_GUST = "wind_gust"
    STORM = "storm"
