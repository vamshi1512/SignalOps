from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.models.enums import WeatherState
from app.schemas.alerts import AlertRead
from app.schemas.common import OrmModel
from app.schemas.fleet import RobotDetail, ZoneRead
from app.schemas.missions import MissionRead


class MetricCard(OrmModel):
    label: str = Field(min_length=2, max_length=80)
    value: float
    delta: float
    suffix: str = ""


class TrendPoint(OrmModel):
    label: str = Field(min_length=2, max_length=24)
    value: float


class DistributionPoint(OrmModel):
    label: str = Field(min_length=2, max_length=120)
    value: float
    color: str = Field(pattern=r"^#(?:[0-9a-fA-F]{3}){1,2}$")


class WeatherSnapshot(OrmModel):
    state: WeatherState
    intensity: float = Field(ge=0.0, le=1.0)
    updated_at: datetime


class ActivityItem(OrmModel):
    id: str
    timestamp: datetime
    category: str = Field(min_length=2, max_length=64)
    title: str = Field(min_length=2, max_length=160)
    detail: str = Field(min_length=4, max_length=1_000)
    robot_name: str | None = None


class DashboardOverview(OrmModel):
    generated_at: datetime
    metrics: list[MetricCard]
    fleet_status_distribution: list[DistributionPoint]
    battery_trend: list[TrendPoint]
    utilization_trend: list[TrendPoint]
    mission_area_trend: list[TrendPoint]
    alert_frequency_trend: list[TrendPoint]
    downtime_by_robot: list[DistributionPoint]
    robots: list[RobotDetail]
    zones: list[ZoneRead]
    active_alerts: list[AlertRead]
    active_missions: list[MissionRead]
    activity: list[ActivityItem]
    weather: WeatherSnapshot
