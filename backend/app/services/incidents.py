from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import IncidentStatus, SeverityLevel
from app.models.incident import Incident, IncidentNote
from app.models.service import Service
from app.models.user import User
from app.repositories.incidents import IncidentRepository
from app.repositories.logs import LogRepository
from app.utils.incidenting import root_cause_hint


class IncidentService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = IncidentRepository(session)
        self.log_repository = LogRepository(session)

    async def group_log(
        self,
        *,
        service: Service,
        group_key: str,
        severity: SeverityLevel,
        message: str,
        metadata: dict[str, str],
        occurred_at: datetime,
    ) -> Incident:
        incident = await self.repository.get_open_by_group_key(group_key)
        one_hour_ago = occurred_at - timedelta(hours=1)
        errors = await self.log_repository.count_by_severity(
            service_id=service.id,
            severities=[SeverityLevel.ERROR, SeverityLevel.CRITICAL],
            start_at=one_hour_ago,
            end_at=occurred_at,
        )
        total = await self.log_repository.count_total(
            service_id=service.id,
            start_at=one_hour_ago,
            end_at=occurred_at,
        )
        error_rate = round((errors / total) * 100, 2) if total else 0.0
        health_impact = min(100.0, round(error_rate * 1.8 + errors * 2.5, 2))

        if incident:
            incident.last_seen_at = occurred_at
            incident.occurrence_count += 1
            incident.affected_logs += 1
            incident.current_error_rate = error_rate
            incident.health_impact = health_impact
            if severity == SeverityLevel.CRITICAL:
                incident.severity = SeverityLevel.CRITICAL
            return incident

        incident = Incident(
            service_id=service.id,
            title=f"{service.name}: {message[:80]}",
            summary=f"Repeated {severity.value} log cluster detected for {service.name}.",
            root_cause_hint=root_cause_hint(message, metadata),
            status=IncidentStatus.OPEN,
            severity=severity,
            environment=service.environment,
            group_key=group_key,
            first_seen_at=occurred_at,
            last_seen_at=occurred_at,
            occurrence_count=1,
            affected_logs=1,
            current_error_rate=error_rate,
            health_impact=health_impact,
        )
        await self.repository.add(incident)
        await self.repository.add_note(
            IncidentNote(
                incident=incident,
                content=f"SignalOps auto-grouped repeated {severity.value} logs into an incident.",
                is_system=True,
            )
        )
        return incident

    async def update_incident(
        self,
        incident: Incident,
        *,
        assignee_id: str | None = None,
        severity: SeverityLevel | None = None,
        status: IncidentStatus | None = None,
        summary: str | None = None,
    ) -> Incident:
        if assignee_id is not None:
            incident.assignee_id = assignee_id
        if severity:
            incident.severity = severity
        if status:
            incident.status = status
            if status == IncidentStatus.RESOLVED:
                incident.resolved_at = datetime.now(timezone.utc)
        if summary is not None:
            incident.summary = summary
        await self.repository.add_note(
            IncidentNote(
                incident=incident,
                content=f"Incident updated. Status={incident.status.value}, severity={incident.severity.value}.",
                is_system=True,
            )
        )
        return incident

    async def add_note(self, incident: Incident, author: User, content: str) -> IncidentNote:
        note = IncidentNote(incident=incident, author_id=author.id, content=content, is_system=False)
        return await self.repository.add_note(note)

