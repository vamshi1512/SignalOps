from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.alerting import AlertRule
from app.models.enums import AlertMetric, ServiceEnvironment, ServicePriority, SeverityLevel, UserRole
from app.models.service import Service
from app.models.user import User
from app.repositories.alerts import AlertRepository
from app.repositories.services import ServiceRepository
from app.repositories.users import UserRepository
from app.services.ingestion import LogIngestionService


SERVICES = [
    {
        "name": "Payment API",
        "slug": "payment-api",
        "owner": "Team Atlas",
        "environment": ServiceEnvironment.PRODUCTION,
        "priority": ServicePriority.P0,
        "sla_target": 99.95,
        "description": "High-throughput payment orchestration and settlement pipeline.",
    },
    {
        "name": "Checkout Web",
        "slug": "checkout-web",
        "owner": "Team Horizon",
        "environment": ServiceEnvironment.PRODUCTION,
        "priority": ServicePriority.P1,
        "sla_target": 99.9,
        "description": "Customer checkout frontend and session orchestration.",
    },
    {
        "name": "Identity Service",
        "slug": "identity-service",
        "owner": "Team Lockstep",
        "environment": ServiceEnvironment.PRODUCTION,
        "priority": ServicePriority.P0,
        "sla_target": 99.95,
        "description": "Authentication, token minting, and RBAC policy enforcement.",
    },
    {
        "name": "Fulfillment Engine",
        "slug": "fulfillment-engine",
        "owner": "Team Vector",
        "environment": ServiceEnvironment.PRODUCTION,
        "priority": ServicePriority.P1,
        "sla_target": 99.9,
        "description": "Post-order orchestration for warehouse dispatch and reconciliation.",
    },
    {
        "name": "Notification Worker",
        "slug": "notification-worker",
        "owner": "Team Orbit",
        "environment": ServiceEnvironment.STAGING,
        "priority": ServicePriority.P2,
        "sla_target": 99.5,
        "description": "Email and push notification fanout worker pipeline.",
    },
]

USERS = [
    ("admin@signalops.dev", "SignalOps Admin", "Admin123!", UserRole.ADMIN),
    ("sre@signalops.dev", "SRE Commander", "Sre123!", UserRole.SRE),
    ("viewer@signalops.dev", "Read Only Observer", "Viewer123!", UserRole.VIEWER),
]

RULES = [
    {
        "service_slug": "payment-api",
        "name": "Payment error rate spike",
        "metric": AlertMetric.ERROR_RATE,
        "threshold": 8.0,
        "window_minutes": 20,
        "severity": SeverityLevel.CRITICAL,
    },
    {
        "service_slug": "identity-service",
        "name": "Auth critical log burst",
        "metric": AlertMetric.CRITICAL_LOGS,
        "threshold": 3,
        "window_minutes": 15,
        "severity": SeverityLevel.CRITICAL,
    },
    {
        "service_slug": "checkout-web",
        "name": "Checkout anomaly detector",
        "metric": AlertMetric.ANOMALY_SCORE,
        "threshold": 2.5,
        "window_minutes": 10,
        "severity": SeverityLevel.WARNING,
    },
]

SCENARIOS = {
    "payment-api": [
        (SeverityLevel.INFO, "settlement batch completed", ["payments", "batch"]),
        (SeverityLevel.WARNING, "gateway latency elevated above internal target", ["payments", "latency"]),
        (SeverityLevel.ERROR, "database timeout while persisting ledger entry", ["payments", "database"]),
        (SeverityLevel.CRITICAL, "card authorization timeout from upstream gateway", ["payments", "timeout"]),
    ],
    "checkout-web": [
        (SeverityLevel.INFO, "checkout session hydrated", ["web", "session"]),
        (SeverityLevel.WARNING, "asset cache miss rate elevated", ["web", "cdn"]),
        (SeverityLevel.ERROR, "checkout API returned 502 for cart validation", ["web", "http"]),
    ],
    "identity-service": [
        (SeverityLevel.INFO, "token refresh issued", ["auth", "token"]),
        (SeverityLevel.ERROR, "unauthorized burst from edge region eu-north", ["auth", "security"]),
        (SeverityLevel.CRITICAL, "postgres authentication replica unavailable", ["auth", "database"]),
    ],
    "fulfillment-engine": [
        (SeverityLevel.INFO, "order handoff completed", ["orders", "queue"]),
        (SeverityLevel.WARNING, "warehouse queue depth approaching threshold", ["orders", "queue"]),
        (SeverityLevel.ERROR, "queue backlog preventing dispatch confirmation", ["orders", "queue"]),
    ],
    "notification-worker": [
        (SeverityLevel.INFO, "email delivery batch flushed", ["notifications", "email"]),
        (SeverityLevel.WARNING, "smtp provider throttle near limit", ["notifications", "provider"]),
        (SeverityLevel.ERROR, "push worker retrying after queue timeout", ["notifications", "queue"]),
    ],
}


class DemoService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.services = ServiceRepository(session)
        self.alerts = AlertRepository(session)
        self.ingestion = LogIngestionService(session)
        self.random = random.Random(42)

    async def seed(self) -> None:
        if await self.users.get_by_email("admin@signalops.dev"):
            return

        for email, full_name, password, role in USERS:
            await self.users.add(
                User(
                    email=email,
                    full_name=full_name,
                    password_hash=hash_password(password),
                    role=role,
                )
            )
        services_by_slug: dict[str, Service] = {}
        for definition in SERVICES:
            service = Service(**definition)
            await self.services.add(service)
            services_by_slug[service.slug] = service

        for rule_definition in RULES:
            service = services_by_slug[rule_definition["service_slug"]]
            await self.alerts.add_rule(
                AlertRule(
                    service_id=service.id,
                    name=rule_definition["name"],
                    description="Seeded demo alert rule",
                    metric=rule_definition["metric"],
                    threshold=rule_definition["threshold"],
                    window_minutes=rule_definition["window_minutes"],
                    severity=rule_definition["severity"],
                    suppression_minutes=20,
                    escalate_after_minutes=15,
                )
            )

        await self.generate_initial_history()

    async def generate_initial_history(self) -> None:
        now = datetime.now(timezone.utc)
        for offset in range(72, 0, -1):
            tick_time = now - timedelta(minutes=offset * 20)
            await self.generate_tick(occurred_at=tick_time, burst=(offset % 11 == 0))

    async def generate_tick(self, *, occurred_at: datetime | None = None, burst: bool = False) -> int:
        occurred_at = occurred_at or datetime.now(timezone.utc)
        count = 0
        services = await self.services.list_all()
        for service in services:
            entries = SCENARIOS[service.slug]
            sample_size = 4 if burst and service.slug in {"payment-api", "identity-service"} else 2
            for severity, message, tags in self.random.sample(entries, k=min(sample_size, len(entries))):
                actual_severity = severity
                if burst and severity == SeverityLevel.WARNING:
                    actual_severity = SeverityLevel.ERROR
                await self.ingestion.ingest(
                    service_slug=service.slug,
                    severity=actual_severity,
                    message=message,
                    source="demo-simulator",
                    tags=tags,
                    metadata={
                        "region": self.random.choice(["us-east-1", "eu-north-1", "eu-west-1"]),
                        "cluster": self.random.choice(["blue", "green", "canary"]),
                        "status_code": str(self.random.choice([200, 401, 429, 500, 502, 503])),
                    },
                    occurred_at=occurred_at,
                )
                count += 1
        return count

