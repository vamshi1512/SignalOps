from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ConnectivityState, MissionStatus, MissionType, OperatingMode, RobotStatus, RobotType, ZoneType
from app.schemas.common import OrmModel, Point, TaskArea


class ZoneRead(OrmModel):
    id: str
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=8, max_length=1_000)
    zone_type: ZoneType
    color: str = Field(pattern=r"^#(?:[0-9a-fA-F]{3}){1,2}$")
    boundary: list[Point] = Field(min_length=3, max_length=32)
    charging_station: Point
    task_areas: list[TaskArea] = Field(default_factory=list, max_length=32)
    weather_exposure: float = Field(ge=0.0, le=3.0)
    is_active: bool


class ZoneSummary(OrmModel):
    id: str
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(min_length=2, max_length=120)
    color: str = Field(pattern=r"^#(?:[0-9a-fA-F]{3}){1,2}$")


class MissionSummary(OrmModel):
    id: str
    name: str = Field(min_length=2, max_length=160)
    mission_type: MissionType
    status: MissionStatus
    progress_pct: float = Field(ge=0.0, le=100.0)
    scheduled_start: datetime | None
    scheduled_end: datetime | None


class RobotRead(OrmModel):
    id: str
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(min_length=2, max_length=120)
    robot_type: RobotType
    model: str = Field(min_length=2, max_length=120)
    serial: str = Field(min_length=3, max_length=120)
    firmware_version: str = Field(min_length=2, max_length=64)
    status: RobotStatus
    operating_mode: OperatingMode
    connectivity_state: ConnectivityState
    position_x: float = Field(ge=0.0, le=5_000.0)
    position_y: float = Field(ge=0.0, le=5_000.0)
    heading_deg: float = Field(ge=-360.0, le=360.0)
    speed_mps: float = Field(ge=0.0, le=20.0)
    battery_level: float = Field(ge=0.0, le=100.0)
    signal_strength: float = Field(ge=0.0, le=100.0)
    tool_state: str = Field(min_length=2, max_length=64)
    status_reason: str = Field(min_length=4, max_length=500)
    total_runtime_minutes: float = Field(ge=0.0)
    total_distance_m: float = Field(ge=0.0)
    charging_cycles: int = Field(ge=0)
    health_score: float = Field(ge=0.0, le=100.0)
    deterministic_seed: int = Field(ge=0)
    last_seen_at: datetime
    created_at: datetime
    updated_at: datetime
    zone: ZoneSummary


class RobotDetail(RobotRead):
    active_mission: MissionSummary | None = None


class RobotCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    robot_type: RobotType
    model: str = Field(min_length=2, max_length=120)
    serial: str = Field(min_length=3, max_length=120)
    firmware_version: str = Field(min_length=2, max_length=64)
    zone_id: str
    battery_level: float = Field(default=100.0, ge=0.0, le=100.0)
    position_x: float = Field(default=0.0, ge=0.0, le=5_000.0)
    position_y: float = Field(default=0.0, ge=0.0, le=5_000.0)
    deterministic_seed: int = Field(default=0, ge=0)


class RobotUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    firmware_version: str | None = Field(default=None, min_length=2, max_length=64)
    zone_id: str | None = None
    status: RobotStatus | None = None
    operating_mode: OperatingMode | None = None
    battery_level: float | None = Field(default=None, ge=0.0, le=100.0)
    position_x: float | None = Field(default=None, ge=0.0, le=5_000.0)
    position_y: float | None = Field(default=None, ge=0.0, le=5_000.0)
    status_reason: str | None = Field(default=None, min_length=4, max_length=500)
