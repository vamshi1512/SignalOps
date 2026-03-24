from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import NotificationChannel, NotificationStatus, ResultStatus, RunStatus, TriggerType
from app.schemas.auth import UserRead
from app.schemas.qa import EnvironmentRead, FixtureSetRead, ProjectRead, ScheduleRead, SuiteSummaryRead


class ManualRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    environment_id: str | None = None
    fixture_set_id: str | None = None
    parallel_workers: Annotated[int | None, Field(default=None, ge=1, le=16)] = None


class AttachmentRead(BaseModel):
    label: str
    type: Literal["image", "json", "text"]
    url: str


class TestResultRead(BaseModel):
    id: str
    test_case_id: str | None
    name: str
    module_name: str
    status: ResultStatus
    retry_count: int
    is_flaky: bool
    duration_ms: int
    started_at: datetime
    finished_at: datetime
    error_message: str
    stack_trace: str
    logs: str
    request_details: dict[str, Any] = Field(default_factory=dict)
    response_details: dict[str, Any] = Field(default_factory=dict)
    attachments: list[AttachmentRead] = Field(default_factory=list)


class NotificationRead(BaseModel):
    id: str
    channel: NotificationChannel
    status: NotificationStatus
    recipient: str
    subject: str
    message: str
    delivered_at: datetime | None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class TestRunRead(BaseModel):
    id: str
    trigger_type: TriggerType
    status: RunStatus
    requested_parallel_workers: int
    total_count: int
    pass_count: int
    fail_count: int
    skip_count: int
    flaky_count: int
    duration_ms: int
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    summary: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    project: ProjectRead
    suite: SuiteSummaryRead
    environment: EnvironmentRead
    fixture_set: FixtureSetRead | None
    schedule: ScheduleRead | None
    triggered_by: UserRead | None


class TestRunDetail(TestRunRead):
    results: list[TestResultRead] = Field(default_factory=list)
    notifications: list[NotificationRead] = Field(default_factory=list)
