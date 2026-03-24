from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin, utcnow
from app.models.enums import (
    EnvironmentKind,
    EnvironmentStatus,
    NotificationChannel,
    NotificationStatus,
    ResultStatus,
    RunStatus,
    SuiteStatus,
    SuiteType,
    TriggerType,
)


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(160), unique=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    owner: Mapped[str] = mapped_column(String(160))
    repository_url: Mapped[str] = mapped_column(String(255), default="")
    default_branch: Mapped[str] = mapped_column(String(80), default="main")
    description: Mapped[str] = mapped_column(Text, default="")

    environments = relationship("Environment", back_populates="project", cascade="all, delete-orphan")
    fixture_sets = relationship("FixtureSet", back_populates="project", cascade="all, delete-orphan")
    suites = relationship("TestSuite", back_populates="project", cascade="all, delete-orphan")
    runs = relationship("TestRun", back_populates="project")


class Environment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "environments"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(120), index=True)
    kind: Mapped[EnvironmentKind] = mapped_column(Enum(EnvironmentKind), index=True)
    status: Mapped[EnvironmentStatus] = mapped_column(Enum(EnvironmentStatus), default=EnvironmentStatus.HEALTHY, index=True)
    api_base_url: Mapped[str] = mapped_column(String(255))
    ui_base_url: Mapped[str] = mapped_column(String(255))
    health_summary: Mapped[str] = mapped_column(Text, default="")
    variables: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="environments")
    default_for_suites = relationship("TestSuite", back_populates="default_environment")
    schedules = relationship("RunSchedule", back_populates="environment")
    runs = relationship("TestRun", back_populates="environment")


class FixtureSet(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "fixture_sets"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    project = relationship("Project", back_populates="fixture_sets")
    suites = relationship("TestSuite", back_populates="default_fixture_set")
    runs = relationship("TestRun", back_populates="fixture_set")


class TestSuite(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "test_suites"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    default_environment_id: Mapped[str | None] = mapped_column(ForeignKey("environments.id"), nullable=True, index=True)
    default_fixture_set_id: Mapped[str | None] = mapped_column(ForeignKey("fixture_sets.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    suite_type: Mapped[SuiteType] = mapped_column(Enum(SuiteType), index=True)
    owner: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    repo_path: Mapped[str] = mapped_column(String(255), default="")
    command: Mapped[str] = mapped_column(String(255), default="")
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    parallel_workers: Mapped[int] = mapped_column(Integer, default=2)
    status: Mapped[SuiteStatus] = mapped_column(Enum(SuiteStatus), default=SuiteStatus.ACTIVE, index=True)
    is_flaky_watch: Mapped[bool] = mapped_column(Boolean, default=False)

    project = relationship("Project", back_populates="suites")
    default_environment = relationship("Environment", back_populates="default_for_suites")
    default_fixture_set = relationship("FixtureSet", back_populates="suites")
    test_cases = relationship("TestCase", back_populates="suite", cascade="all, delete-orphan", order_by="TestCase.order_index")
    schedules = relationship("RunSchedule", back_populates="suite", cascade="all, delete-orphan")
    runs = relationship("TestRun", back_populates="suite")


class TestCase(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "test_cases"

    suite_id: Mapped[str] = mapped_column(ForeignKey("test_suites.id"), index=True)
    key: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    module_name: Mapped[str] = mapped_column(String(200), index=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    automation_ref: Mapped[str] = mapped_column(String(255), default="")
    expected_outcome: Mapped[str] = mapped_column(Text, default="")
    deterministic_profile: Mapped[str] = mapped_column(String(120), default="stable")
    baseline_duration_ms: Mapped[int] = mapped_column(Integer, default=1000)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    fixture_overrides: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    suite = relationship("TestSuite", back_populates="test_cases")
    results = relationship("TestResult", back_populates="test_case")


class RunSchedule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "run_schedules"

    suite_id: Mapped[str] = mapped_column(ForeignKey("test_suites.id"), index=True)
    environment_id: Mapped[str] = mapped_column(ForeignKey("environments.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    cadence_minutes: Mapped[int] = mapped_column(Integer, default=120)
    next_run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    parallel_workers: Mapped[int] = mapped_column(Integer, default=2)
    timezone: Mapped[str] = mapped_column(String(120), default="UTC")
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    suite = relationship("TestSuite", back_populates="schedules")
    environment = relationship("Environment", back_populates="schedules")
    runs = relationship("TestRun", back_populates="schedule")


class TestRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "test_runs"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    suite_id: Mapped[str] = mapped_column(ForeignKey("test_suites.id"), index=True)
    environment_id: Mapped[str] = mapped_column(ForeignKey("environments.id"), index=True)
    fixture_set_id: Mapped[str | None] = mapped_column(ForeignKey("fixture_sets.id"), nullable=True, index=True)
    schedule_id: Mapped[str | None] = mapped_column(ForeignKey("run_schedules.id"), nullable=True, index=True)
    triggered_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    trigger_type: Mapped[TriggerType] = mapped_column(Enum(TriggerType), default=TriggerType.MANUAL, index=True)
    status: Mapped[RunStatus] = mapped_column(Enum(RunStatus), default=RunStatus.QUEUED, index=True)
    requested_parallel_workers: Mapped[int] = mapped_column(Integer, default=1)
    total_count: Mapped[int] = mapped_column(Integer, default=0)
    pass_count: Mapped[int] = mapped_column(Integer, default=0)
    fail_count: Mapped[int] = mapped_column(Integer, default=0)
    skip_count: Mapped[int] = mapped_column(Integer, default=0)
    flaky_count: Mapped[int] = mapped_column(Integer, default=0)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    summary: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    runtime_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    project = relationship("Project", back_populates="runs")
    suite = relationship("TestSuite", back_populates="runs")
    environment = relationship("Environment", back_populates="runs")
    fixture_set = relationship("FixtureSet", back_populates="runs")
    schedule = relationship("RunSchedule", back_populates="runs")
    triggered_by = relationship("User", back_populates="triggered_runs")
    results = relationship("TestResult", back_populates="run", cascade="all, delete-orphan", order_by="TestResult.started_at")
    notifications = relationship("NotificationEvent", back_populates="run", cascade="all, delete-orphan")


class TestResult(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "test_results"

    run_id: Mapped[str] = mapped_column(ForeignKey("test_runs.id"), index=True)
    suite_id: Mapped[str] = mapped_column(ForeignKey("test_suites.id"), index=True)
    test_case_id: Mapped[str | None] = mapped_column(ForeignKey("test_cases.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    module_name: Mapped[str] = mapped_column(String(200), index=True)
    status: Mapped[ResultStatus] = mapped_column(Enum(ResultStatus), index=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    is_flaky: Mapped[bool] = mapped_column(Boolean, default=False)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    error_message: Mapped[str] = mapped_column(Text, default="")
    stack_trace: Mapped[str] = mapped_column(Text, default="")
    logs: Mapped[str] = mapped_column(Text, default="")
    request_details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    response_details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    attachments: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)

    run = relationship("TestRun", back_populates="results")
    test_case = relationship("TestCase", back_populates="results")


class NotificationEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notification_events"

    run_id: Mapped[str] = mapped_column(ForeignKey("test_runs.id"), index=True)
    channel: Mapped[NotificationChannel] = mapped_column(Enum(NotificationChannel), index=True)
    status: Mapped[NotificationStatus] = mapped_column(Enum(NotificationStatus), default=NotificationStatus.PENDING, index=True)
    recipient: Mapped[str] = mapped_column(String(160))
    subject: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text, default="")
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    run = relationship("TestRun", back_populates="notifications")
