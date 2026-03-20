from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import AlertSeverity, AlertStatus, AlertType
from app.schemas.common import JsonObject, OrmModel, RobotSnapshotSummary
from app.schemas.fleet import MissionSummary


class AlertRead(OrmModel):
    id: str
    type: AlertType
    severity: AlertSeverity
    status: AlertStatus
    title: str = Field(min_length=4, max_length=160)
    message: str = Field(min_length=8, max_length=1_000)
    notes: str = Field(max_length=2_000)
    metadata: JsonObject
    occurred_at: datetime
    acknowledged_at: datetime | None
    resolved_at: datetime | None
    robot: RobotSnapshotSummary
    mission: MissionSummary | None = None


class AlertAcknowledgeRequest(BaseModel):
    notes: str = Field(default="", max_length=500)
