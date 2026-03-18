from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    SRE = "sre"
    VIEWER = "viewer"


class ServiceEnvironment(str, Enum):
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"


class ServicePriority(str, Enum):
    P0 = "p0"
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"


class SeverityLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"


class AlertMetric(str, Enum):
    ERROR_RATE = "error_rate"
    CRITICAL_LOGS = "critical_logs"
    ANOMALY_SCORE = "anomaly_score"
    INCIDENT_COUNT = "incident_count"


class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"
    ESCALATED = "escalated"
    RESOLVED = "resolved"

