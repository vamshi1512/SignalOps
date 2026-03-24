from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, StringConstraints, field_validator, model_validator

from app.models.enums import EnvironmentKind, EnvironmentStatus, RunStatus, SuiteStatus, SuiteType
from app.schemas.common import ORMModel


SlugValue = Annotated[
    str,
    StringConstraints(strip_whitespace=True, to_lower=True, min_length=3, max_length=160, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$"),
]
DisplayName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=160)]
OwnerName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=160)]
BranchName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]
RepoPath = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
CommandValue = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
DescriptionValue = Annotated[str, StringConstraints(strip_whitespace=True, max_length=1_500)]
TagValue = Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True, min_length=2, max_length=32)]


class ProjectCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: DisplayName
    slug: SlugValue
    owner: OwnerName
    repository_url: AnyHttpUrl
    default_branch: BranchName = "main"
    description: DescriptionValue = ""


class ProjectRead(ORMModel):
    id: str
    name: str
    slug: str
    owner: str
    repository_url: str
    default_branch: str
    description: str
    created_at: datetime
    updated_at: datetime


class EnvironmentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: str
    name: DisplayName
    slug: SlugValue
    kind: EnvironmentKind
    status: EnvironmentStatus = EnvironmentStatus.HEALTHY
    api_base_url: AnyHttpUrl
    ui_base_url: AnyHttpUrl
    health_summary: DescriptionValue = ""
    variables: dict[str, str] = Field(default_factory=dict)
    is_default: bool = False

    @field_validator("variables")
    @classmethod
    def normalize_variables(cls, value: dict[str, str]) -> dict[str, str]:
        return {key.strip().upper(): item.strip() for key, item in value.items() if key.strip() and item.strip()}


class EnvironmentRead(ORMModel):
    id: str
    project_id: str
    name: str
    slug: str
    kind: EnvironmentKind
    status: EnvironmentStatus
    api_base_url: str
    ui_base_url: str
    health_summary: str
    variables: dict[str, str]
    is_default: bool
    last_checked_at: datetime | None
    created_at: datetime
    updated_at: datetime


class FixtureSetCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: str
    name: DisplayName
    description: DescriptionValue = ""
    payload: dict[str, Any] = Field(default_factory=dict)


class FixtureSetRead(ORMModel):
    id: str
    project_id: str
    name: str
    description: str
    payload: dict[str, object]
    created_at: datetime
    updated_at: datetime


class SuiteCaseRead(ORMModel):
    id: str
    key: str
    name: str
    module_name: str
    order_index: int
    automation_ref: str
    expected_outcome: str
    deterministic_profile: str
    baseline_duration_ms: int
    tags: list[str]
    fixture_overrides: dict[str, Any]


class ScheduleRead(ORMModel):
    id: str
    suite_id: str
    environment_id: str
    name: str
    cadence_minutes: int
    next_run_at: datetime
    last_run_at: datetime | None
    parallel_workers: int
    timezone: str
    active: bool
    environment_name: str


class ScheduleUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    active: bool | None = None
    cadence_minutes: int | None = Field(default=None, ge=15, le=1_440)
    parallel_workers: int | None = Field(default=None, ge=1, le=16)
    next_run_at: datetime | None = None

    @model_validator(mode="after")
    def validate_update_payload(self) -> "ScheduleUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("At least one schedule field must be provided")
        if self.next_run_at and self.next_run_at.tzinfo is None:
            raise ValueError("next_run_at must include timezone information")
        return self


class SuiteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: str
    default_environment_id: str | None = None
    default_fixture_set_id: str | None = None
    name: DisplayName
    slug: SlugValue
    suite_type: SuiteType
    owner: OwnerName
    description: DescriptionValue = ""
    repo_path: RepoPath
    command: CommandValue
    tags: list[TagValue] = Field(default_factory=list, max_length=12)
    parallel_workers: int = Field(default=2, ge=1, le=16)
    status: SuiteStatus = SuiteStatus.ACTIVE
    is_flaky_watch: bool = False

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        normalized = []
        for tag in tags:
            value = tag.strip().lower()
            if value and value not in normalized:
                normalized.append(value)
        return normalized


class SuiteSummaryRead(ORMModel):
    id: str
    name: str
    slug: str
    suite_type: SuiteType
    owner: str
    tags: list[str]
    status: SuiteStatus


class SuiteRead(ORMModel):
    id: str
    name: str
    slug: str
    suite_type: SuiteType
    owner: str
    description: str
    repo_path: str
    command: str
    tags: list[str]
    parallel_workers: int
    status: SuiteStatus
    is_flaky_watch: bool
    created_at: datetime
    updated_at: datetime
    project: ProjectRead
    default_environment: EnvironmentRead | None
    default_fixture_set: FixtureSetRead | None
    test_cases: list[SuiteCaseRead]
    schedules: list[ScheduleRead]
    latest_run_status: RunStatus | None = None
    last_run_at: datetime | None = None
    pass_rate_14d: float = 0.0
    flaky_cases: int = 0
