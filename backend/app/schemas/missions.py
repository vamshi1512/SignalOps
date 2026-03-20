from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.models.enums import MissionStatus, MissionType
from app.schemas.common import OrmModel, Point, RobotSnapshotSummary
from app.schemas.fleet import ZoneSummary


class CommandQueueEntry(OrmModel):
    command: str = Field(min_length=3, max_length=64)
    by: str = Field(min_length=2, max_length=120)
    note: str = Field(default="", max_length=240)
    timestamp: datetime


class MissionRead(OrmModel):
    id: str
    name: str = Field(min_length=2, max_length=160)
    mission_type: MissionType
    status: MissionStatus
    scheduled_start: datetime | None
    scheduled_end: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    estimated_duration_minutes: float = Field(ge=1.0, le=1_440.0)
    progress_pct: float = Field(ge=0.0, le=100.0)
    target_area_sqm: float = Field(ge=0.0, le=250_000.0)
    completed_area_sqm: float = Field(ge=0.0, le=250_000.0)
    command_queue: list[CommandQueueEntry] = Field(default_factory=list, max_length=128)
    route_points: list[Point] = Field(default_factory=list, min_length=2, max_length=512)
    replay_seed: int = Field(ge=0)
    operator_notes: str = Field(max_length=2_000)
    created_at: datetime
    updated_at: datetime
    robot: RobotSnapshotSummary
    zone: ZoneSummary


class MissionDetail(MissionRead):
    pass


class MissionCreate(BaseModel):
    robot_id: str
    zone_id: str
    name: str = Field(min_length=2, max_length=160)
    mission_type: MissionType
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    estimated_duration_minutes: float = Field(default=45.0, ge=1.0, le=1_440.0)
    target_area_sqm: float = Field(default=0.0, ge=0.0, le=250_000.0)
    operator_notes: str = Field(default="", max_length=2_000)

    @model_validator(mode="after")
    def validate_schedule(self) -> MissionCreate:
        if self.scheduled_start and self.scheduled_end and self.scheduled_end <= self.scheduled_start:
            raise ValueError("scheduled_end must be later than scheduled_start")
        return self


class MissionCommandRequest(BaseModel):
    command: str = Field(pattern="^(pause|resume|return_to_base|emergency_stop|manual_override|clear_override)$")
    note: str | None = Field(default=None, max_length=240)
