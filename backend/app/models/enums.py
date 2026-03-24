from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    QA_ENGINEER = "qa_engineer"
    VIEWER = "viewer"


class EnvironmentKind(str, Enum):
    QA = "qa"
    STAGING = "staging"
    PROD_LIKE = "prod_like"
    MOCK = "mock"


class EnvironmentStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"


class SuiteType(str, Enum):
    API = "api"
    UI = "ui"


class SuiteStatus(str, Enum):
    ACTIVE = "active"
    DRAFT = "draft"
    PAUSED = "paused"


class RunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


class ResultStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    FLAKY = "flaky"


class TriggerType(str, Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    DEMO = "demo"


class NotificationChannel(str, Enum):
    SLACK = "slack"
    EMAIL = "email"
    WEBHOOK = "webhook"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    SKIPPED = "skipped"
