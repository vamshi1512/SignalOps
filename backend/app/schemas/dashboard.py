from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import EnvironmentKind, EnvironmentStatus, RunStatus, SuiteType
from app.schemas.common import TimeSeriesPoint
from app.schemas.execution import TestRunRead


class MetricCard(BaseModel):
    label: str
    value: float
    delta: float
    suffix: str


class FailureBreakdown(BaseModel):
    module_name: str
    failures: int


class SuiteRiskRead(BaseModel):
    id: str
    name: str
    suite_type: SuiteType
    owner: str
    latest_status: RunStatus | None
    pass_rate_14d: float
    flaky_cases: int
    failing_results: int
    environment_name: str | None


class EnvironmentBadgeRead(BaseModel):
    id: str
    name: str
    kind: EnvironmentKind
    status: EnvironmentStatus
    project_name: str
    last_checked_at: datetime | None


class DashboardOverview(BaseModel):
    metrics: list[MetricCard] = Field(default_factory=list)
    pass_rate_trend: list[TimeSeriesPoint] = Field(default_factory=list)
    duration_trend: list[TimeSeriesPoint] = Field(default_factory=list)
    flaky_trend: list[TimeSeriesPoint] = Field(default_factory=list)
    failures_by_module: list[FailureBreakdown] = Field(default_factory=list)
    recent_runs: list[TestRunRead] = Field(default_factory=list)
    suites_at_risk: list[SuiteRiskRead] = Field(default_factory=list)
    environments: list[EnvironmentBadgeRead] = Field(default_factory=list)
