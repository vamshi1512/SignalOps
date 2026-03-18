from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import IncidentStatus, ServiceEnvironment, SeverityLevel
from app.schemas.auth import UserRead
from app.schemas.common import ORMModel
from app.schemas.services import ServiceRead


class IncidentNoteCreate(BaseModel):
    content: str = Field(min_length=3, max_length=4000)


class IncidentNoteRead(ORMModel):
    id: str
    content: str
    is_system: bool
    created_at: datetime
    author: UserRead | None = None


class IncidentUpdate(BaseModel):
    assignee_id: str | None = None
    severity: SeverityLevel | None = None
    status: IncidentStatus | None = None
    summary: str | None = None


class IncidentRead(ORMModel):
    id: str
    title: str
    summary: str
    root_cause_hint: str
    status: IncidentStatus
    severity: SeverityLevel
    environment: ServiceEnvironment
    group_key: str
    first_seen_at: datetime
    last_seen_at: datetime
    resolved_at: datetime | None
    occurrence_count: int
    affected_logs: int
    current_error_rate: float
    health_impact: float
    service: ServiceRead
    assignee: UserRead | None = None
    notes: list[IncidentNoteRead] = Field(default_factory=list)
