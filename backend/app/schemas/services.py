from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ServiceEnvironment, ServicePriority
from app.schemas.common import ORMModel


class ServiceCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    slug: str = Field(min_length=3, max_length=120, pattern=r"^[a-z0-9-]+$")
    owner: str = Field(min_length=3, max_length=120)
    environment: ServiceEnvironment
    priority: ServicePriority
    sla_target: float = Field(ge=90.0, le=99.999)
    description: str = ""


class ServiceRead(ORMModel):
    id: str
    name: str
    slug: str
    owner: str
    environment: ServiceEnvironment
    priority: ServicePriority
    sla_target: float
    description: str
    created_at: datetime
    updated_at: datetime
    health_score: float = 100.0
    open_incidents: int = 0
    open_alerts: int = 0

