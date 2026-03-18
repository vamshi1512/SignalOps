from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SeverityLevel
from app.models.log_event import LogEvent
from app.repositories.logs import LogRepository
from app.repositories.services import ServiceRepository
from app.services.alerts import AlertService
from app.services.incidents import IncidentService
from app.services.log_store import PostgresLogStorage


class LogIngestionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.service_repository = ServiceRepository(session)
        self.log_repository = LogRepository(session)
        self.log_store = PostgresLogStorage(session)
        self.incident_service = IncidentService(session)
        self.alert_service = AlertService(session)

    async def ingest(
        self,
        *,
        service_slug: str,
        severity: SeverityLevel,
        message: str,
        source: str,
        tags: list[str],
        metadata: dict[str, Any],
        occurred_at: datetime | None = None,
    ) -> tuple[LogEvent, str | None, list[str]]:
        service = await self.service_repository.get_by_slug(service_slug)
        if not service:
            raise ValueError(f"Unknown service slug '{service_slug}'")
        occurred_at = occurred_at or datetime.now(timezone.utc)

        log_event = await self.log_store.ingest(
            service=service,
            severity=severity,
            message=message,
            source=source,
            tags=tags,
            metadata=metadata,
            occurred_at=occurred_at,
        )
        anomaly_score = await self._anomaly_score(service.id, occurred_at)
        log_event.anomaly_score = anomaly_score
        log_event.is_anomalous = anomaly_score >= 2.5

        incident = None
        if severity in {SeverityLevel.ERROR, SeverityLevel.CRITICAL}:
            incident = await self.incident_service.group_log(
                service=service,
                group_key=log_event.fingerprint,
                severity=severity,
                message=message,
                metadata={str(key): str(value) for key, value in metadata.items()},
                occurred_at=occurred_at,
            )

        alerts = await self.alert_service.evaluate_rules(
            service=service,
            incident=incident,
            occurred_at=occurred_at,
            anomaly_score=anomaly_score,
        )

        return log_event, incident.id if incident else None, [alert.id for alert in alerts]

    async def _anomaly_score(self, service_id: str, occurred_at: datetime) -> float:
        window = timedelta(minutes=10)
        current_start = occurred_at - window
        baseline_end = current_start
        baseline_start = baseline_end - (window * 3)

        current_errors = await self.log_repository.count_by_severity(
            service_id=service_id,
            severities=[SeverityLevel.ERROR, SeverityLevel.CRITICAL],
            start_at=current_start,
            end_at=occurred_at,
        )
        baseline_errors = await self.log_repository.count_by_severity(
            service_id=service_id,
            severities=[SeverityLevel.ERROR, SeverityLevel.CRITICAL],
            start_at=baseline_start,
            end_at=baseline_end,
        )
        expected = max(1.0, baseline_errors / 3 if baseline_errors else 1.0)
        return round(current_errors / expected, 2)
