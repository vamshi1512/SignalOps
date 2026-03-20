from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.models.enums import ConnectivityState, OperatingMode, RobotStatus, WeatherState
from app.schemas.alerts import AlertRead
from app.schemas.common import JsonObject, OrmModel
from app.schemas.fleet import RobotDetail
from app.schemas.missions import MissionRead


class TelemetryPointRead(OrmModel):
    id: str
    recorded_at: datetime
    position_x: float = Field(ge=0.0, le=5_000.0)
    position_y: float = Field(ge=0.0, le=5_000.0)
    battery_level: float = Field(ge=0.0, le=100.0)
    speed_mps: float = Field(ge=0.0, le=20.0)
    mission_progress_pct: float = Field(ge=0.0, le=100.0)
    connectivity_state: ConnectivityState
    robot_status: RobotStatus
    operating_mode: OperatingMode
    weather_state: WeatherState
    payload: JsonObject


class MissionEventRead(OrmModel):
    id: str
    occurred_at: datetime
    category: str = Field(min_length=2, max_length=64)
    event_type: str = Field(min_length=2, max_length=120)
    message: str = Field(min_length=4, max_length=1_000)
    payload: JsonObject


class RobotHistoryRead(OrmModel):
    robot: RobotDetail
    telemetry: list[TelemetryPointRead]
    events: list[MissionEventRead]
    missions: list[MissionRead]
    alerts: list[AlertRead]


class MissionReplayRead(OrmModel):
    mission: MissionRead
    telemetry: list[TelemetryPointRead]
    events: list[MissionEventRead]
