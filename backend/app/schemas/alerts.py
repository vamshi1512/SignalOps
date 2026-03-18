from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import AlertMetric, AlertStatus, SeverityLevel
from app.schemas.common import ORMModel
from app.schemas.incidents import IncidentRead
from app.schemas.services import ServiceRead


class AlertRuleCreate(BaseModel):
    service_id: str | None = None
    name: str = Field(min_length=3, max_length=140)
    description: str = ""
    metric: AlertMetric
    threshold: float = Field(gt=0)
    window_minutes: int = Field(ge=1, le=1440)
    severity: SeverityLevel
    suppression_minutes: int = Field(ge=1, le=1440, default=15)
    escalate_after_minutes: int = Field(ge=1, le=1440, default=20)


class AlertRuleRead(ORMModel):
    id: str
    name: str
    description: str
    metric: AlertMetric
    threshold: float
    window_minutes: int
    severity: SeverityLevel
    enabled: bool
    suppression_minutes: int
    escalate_after_minutes: int
    service: ServiceRead | None = None


class AlertRead(ORMModel):
    id: str
    status: AlertStatus
    message: str
    current_value: float
    threshold: float
    triggered_at: datetime
    acknowledged_at: datetime | None
    resolved_at: datetime | None
    suppressed_until: datetime | None
    escalation_level: int
    service: ServiceRead
    rule: AlertRuleRead
    incident: IncidentRead | None = None


class SuppressRequest(BaseModel):
    minutes: int = Field(ge=1, le=1440, default=30)

