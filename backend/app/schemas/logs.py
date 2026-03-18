from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, Field

from app.models.enums import SeverityLevel
from app.schemas.common import ORMModel
from app.schemas.services import ServiceRead


class LogIngestRequest(BaseModel):
    service_slug: str = Field(min_length=3, max_length=120)
    severity: SeverityLevel
    message: str = Field(min_length=5, max_length=4000)
    source: str = Field(default="application", max_length=120)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime | None = None


class LogEventRead(ORMModel):
    id: str
    occurred_at: datetime
    severity: SeverityLevel
    message: str
    source: str
    tags: list[str]
    metadata: dict[str, Any] = Field(
        validation_alias=AliasChoices("event_metadata"),
        serialization_alias="metadata",
    )
    fingerprint: str
    anomaly_score: float
    is_anomalous: bool
    service: ServiceRead


class LogIngestResponse(BaseModel):
    log: LogEventRead
    incident_id: str | None = None
    alert_ids: list[str] = Field(default_factory=list)
