from __future__ import annotations

from pydantic import BaseModel

from app.schemas.alerts import AlertRead
from app.schemas.common import TimeSeriesPoint
from app.schemas.incidents import IncidentRead
from app.schemas.services import ServiceRead


class MetricCard(BaseModel):
    label: str
    value: float
    delta: float
    suffix: str = ""


class DashboardOverview(BaseModel):
    metrics: list[MetricCard]
    incident_trend: list[TimeSeriesPoint]
    error_rate_trend: list[TimeSeriesPoint]
    alert_volume_trend: list[TimeSeriesPoint]
    services: list[ServiceRead]
    recent_incidents: list[IncidentRead]
    active_alerts: list[AlertRead]

