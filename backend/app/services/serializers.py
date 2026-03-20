from __future__ import annotations

from app.models.alert import Alert
from app.models.audit import AuditEntry
from app.models.mission import Mission
from app.models.mission_event import MissionEvent
from app.models.robot import Robot
from app.models.telemetry import TelemetrySnapshot
from app.models.user import User
from app.models.zone import Zone


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "title": user.title,
        "role": user.role,
        "theme_preference": user.theme_preference,
        "settings": user.settings,
        "is_active": user.is_active,
    }


def serialize_zone(zone: Zone) -> dict:
    return {
        "id": zone.id,
        "name": zone.name,
        "slug": zone.slug,
        "description": zone.description,
        "zone_type": zone.zone_type,
        "color": zone.color,
        "boundary": zone.boundary,
        "charging_station": zone.charging_station,
        "task_areas": zone.task_areas,
        "weather_exposure": zone.weather_exposure,
        "is_active": zone.is_active,
    }


def serialize_zone_summary(zone: Zone) -> dict:
    return {"id": zone.id, "name": zone.name, "slug": zone.slug, "color": zone.color}


def serialize_mission_summary(mission: Mission) -> dict:
    return {
        "id": mission.id,
        "name": mission.name,
        "mission_type": mission.mission_type.value,
        "status": mission.status.value,
        "progress_pct": round(mission.progress_pct, 1),
        "scheduled_start": mission.scheduled_start,
        "scheduled_end": mission.scheduled_end,
    }


def serialize_robot(robot: Robot, active_mission: Mission | None = None) -> dict:
    return {
        "id": robot.id,
        "name": robot.name,
        "slug": robot.slug,
        "robot_type": robot.robot_type,
        "model": robot.model,
        "serial": robot.serial,
        "firmware_version": robot.firmware_version,
        "status": robot.status,
        "operating_mode": robot.operating_mode,
        "connectivity_state": robot.connectivity_state,
        "position_x": round(robot.position_x, 2),
        "position_y": round(robot.position_y, 2),
        "heading_deg": round(robot.heading_deg, 1),
        "speed_mps": round(robot.speed_mps, 2),
        "battery_level": round(robot.battery_level, 1),
        "signal_strength": round(robot.signal_strength, 1),
        "tool_state": robot.tool_state,
        "status_reason": robot.status_reason,
        "total_runtime_minutes": round(robot.total_runtime_minutes, 1),
        "total_distance_m": round(robot.total_distance_m, 1),
        "charging_cycles": robot.charging_cycles,
        "health_score": round(robot.health_score, 1),
        "deterministic_seed": robot.deterministic_seed,
        "last_seen_at": robot.last_seen_at,
        "created_at": robot.created_at,
        "updated_at": robot.updated_at,
        "zone": serialize_zone_summary(robot.zone),
        "active_mission": serialize_mission_summary(active_mission) if active_mission else None,
    }


def serialize_mission(mission: Mission) -> dict:
    return {
        "id": mission.id,
        "name": mission.name,
        "mission_type": mission.mission_type,
        "status": mission.status,
        "scheduled_start": mission.scheduled_start,
        "scheduled_end": mission.scheduled_end,
        "started_at": mission.started_at,
        "completed_at": mission.completed_at,
        "estimated_duration_minutes": mission.estimated_duration_minutes,
        "progress_pct": round(mission.progress_pct, 1),
        "target_area_sqm": round(mission.target_area_sqm, 1),
        "completed_area_sqm": round(mission.completed_area_sqm, 1),
        "command_queue": mission.command_queue,
        "route_points": mission.route_points,
        "replay_seed": mission.replay_seed,
        "operator_notes": mission.operator_notes,
        "created_at": mission.created_at,
        "updated_at": mission.updated_at,
        "robot": {
            "id": mission.robot.id,
            "name": mission.robot.name,
            "status": mission.robot.status,
            "battery_level": round(mission.robot.battery_level, 1),
        },
        "zone": serialize_zone_summary(mission.zone),
    }


def serialize_alert(alert: Alert) -> dict:
    return {
        "id": alert.id,
        "type": alert.type,
        "severity": alert.severity,
        "status": alert.status,
        "title": alert.title,
        "message": alert.message,
        "notes": alert.notes,
        "metadata": alert.context,
        "occurred_at": alert.occurred_at,
        "acknowledged_at": alert.acknowledged_at,
        "resolved_at": alert.resolved_at,
        "robot": {
            "id": alert.robot.id,
            "name": alert.robot.name,
            "status": alert.robot.status,
            "battery_level": round(alert.robot.battery_level, 1),
        },
        "mission": serialize_mission_summary(alert.mission) if alert.mission else None,
    }


def serialize_event(event: MissionEvent) -> dict:
    return {
        "id": event.id,
        "occurred_at": event.occurred_at,
        "category": event.category,
        "event_type": event.event_type,
        "message": event.message,
        "payload": event.payload,
    }


def serialize_telemetry(snapshot: TelemetrySnapshot) -> dict:
    return {
        "id": snapshot.id,
        "recorded_at": snapshot.recorded_at,
        "position_x": round(snapshot.position_x, 2),
        "position_y": round(snapshot.position_y, 2),
        "battery_level": round(snapshot.battery_level, 1),
        "speed_mps": round(snapshot.speed_mps, 2),
        "mission_progress_pct": round(snapshot.mission_progress_pct, 1),
        "connectivity_state": snapshot.connectivity_state.value,
        "robot_status": snapshot.robot_status.value,
        "operating_mode": snapshot.operating_mode.value,
        "weather_state": snapshot.weather_state.value,
        "payload": snapshot.payload,
    }


def serialize_audit(entry: AuditEntry) -> dict:
    return {
        "id": entry.id,
        "actor_id": entry.actor_id,
        "actor_email": entry.actor_email,
        "action": entry.action,
        "resource_type": entry.resource_type,
        "resource_id": entry.resource_id,
        "message": entry.message,
        "details": entry.details,
        "created_at": entry.created_at,
    }
