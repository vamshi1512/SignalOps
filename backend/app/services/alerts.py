from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alerting import Alert, AlertRule
from app.models.enums import AlertMetric, AlertStatus, SeverityLevel
from app.models.incident import Incident
from app.models.service import Service
from app.models.user import User
from app.repositories.alerts import AlertRepository
from app.repositories.incidents import IncidentRepository
from app.repositories.logs import LogRepository
from app.services.audit import AuditService


class AlertService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = AlertRepository(session)
        self.log_repository = LogRepository(session)
        self.incident_repository = IncidentRepository(session)
        self.audit = AuditService(session)

    async def evaluate_rules(
        self,
        *,
        service: Service,
        incident: Incident | None,
        occurred_at: datetime,
        anomaly_score: float,
    ) -> list[Alert]:
        rules = await self.repository.list_rules()
        service_rules = [rule for rule in rules if rule.enabled and (rule.service_id in (None, service.id))]
        alerts: list[Alert] = []
        for rule in service_rules:
            current_value = await self._metric_value(rule, service.id, occurred_at, anomaly_score)
            if current_value < rule.threshold:
                continue
            active = await self.repository.find_active_for_rule(rule.id)
            if active and active.suppressed_until and active.suppressed_until > occurred_at:
                active.status = AlertStatus.SUPPRESSED
                continue
            if active:
                active.current_value = current_value
                active.status = AlertStatus.ESCALATED if active.escalation_level > 0 else active.status
                alerts.append(active)
                continue
            alert = Alert(
                rule_id=rule.id,
                service_id=service.id,
                incident_id=incident.id if incident else None,
                status=AlertStatus.OPEN,
                message=f"{rule.name} breached for {service.name}",
                current_value=current_value,
                threshold=rule.threshold,
                triggered_at=occurred_at,
            )
            await self.repository.add(alert)
            await self.audit.record(
                action="alert.triggered",
                resource_type="alert",
                resource_id=alert.id,
                message=f"Alert '{rule.name}' opened for {service.name}",
                details={"metric": rule.metric.value, "threshold": str(rule.threshold)},
            )
            alerts.append(alert)
        return alerts

    async def _metric_value(
        self,
        rule: AlertRule,
        service_id: str,
        occurred_at: datetime,
        anomaly_score: float,
    ) -> float:
        start_at = occurred_at - timedelta(minutes=rule.window_minutes)
        if rule.metric == AlertMetric.ERROR_RATE:
            errors = await self.log_repository.count_by_severity(
                service_id=service_id,
                severities=[SeverityLevel.ERROR, SeverityLevel.CRITICAL],
                start_at=start_at,
                end_at=occurred_at,
            )
            total = await self.log_repository.count_total(service_id=service_id, start_at=start_at, end_at=occurred_at)
            return round((errors / total) * 100, 2) if total else 0.0
        if rule.metric == AlertMetric.CRITICAL_LOGS:
            return float(
                await self.log_repository.count_by_severity(
                    service_id=service_id,
                    severities=[SeverityLevel.CRITICAL],
                    start_at=start_at,
                    end_at=occurred_at,
                )
            )
        if rule.metric == AlertMetric.ANOMALY_SCORE:
            return anomaly_score
        return float(await self.incident_repository.count_in_window(service_id=service_id, start_at=start_at, end_at=occurred_at))

    async def acknowledge(self, alert: Alert, actor: User) -> Alert:
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now(timezone.utc)
        await self.audit.record(
            action="alert.acknowledged",
            resource_type="alert",
            resource_id=alert.id,
            actor=actor,
            message=f"{actor.full_name} acknowledged alert {alert.id}",
        )
        return alert

    async def suppress(self, alert: Alert, actor: User, minutes: int) -> Alert:
        alert.status = AlertStatus.SUPPRESSED
        alert.suppressed_until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        await self.audit.record(
            action="alert.suppressed",
            resource_type="alert",
            resource_id=alert.id,
            actor=actor,
            message=f"{actor.full_name} suppressed alert {alert.id} for {minutes} minutes",
        )
        return alert

    async def process_escalations(self) -> int:
        rules = await self.repository.list_rules()
        rules_by_id = {rule.id: rule for rule in rules}
        alerts = await self.repository.list_alerts()
        now = datetime.now(timezone.utc)
        escalated = 0
        for alert in alerts:
            if alert.status not in {AlertStatus.OPEN, AlertStatus.ACKNOWLEDGED}:
                continue
            rule = rules_by_id.get(alert.rule_id)
            if not rule:
                continue
            if now - alert.triggered_at >= timedelta(minutes=rule.escalate_after_minutes):
                alert.status = AlertStatus.ESCALATED
                alert.escalation_level += 1
                escalated += 1
                await self.audit.record(
                    action="alert.escalated",
                    resource_type="alert",
                    resource_id=alert.id,
                    message=f"Alert {alert.id} escalated to level {alert.escalation_level}",
                )
        return escalated

