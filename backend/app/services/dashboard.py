from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SeverityLevel
from app.repositories.alerts import AlertRepository
from app.repositories.incidents import IncidentRepository
from app.repositories.logs import LogRepository
from app.repositories.services import ServiceRepository
from app.schemas.dashboard import DashboardOverview, MetricCard
from app.schemas.common import TimeSeriesPoint
from app.schemas.services import ServiceRead


class DashboardService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.alerts = AlertRepository(session)
        self.incidents = IncidentRepository(session)
        self.logs = LogRepository(session)
        self.services = ServiceRepository(session)

    async def overview(self) -> DashboardOverview:
        services = await self.services.list_all()
        service_cards: list[ServiceRead] = []

        for service in services:
            open_incidents = sum(1 for incident in service.incidents if incident.status.value != "resolved")
            open_alerts = sum(1 for alert in service.alerts if alert.status.value in {"open", "escalated"})
            last_day_total = await self.logs.count_total(
                service_id=service.id,
                start_at=datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0),
                end_at=datetime.now(timezone.utc),
            )
            last_day_errors = await self.logs.count_by_severity(
                service_id=service.id,
                severities=[SeverityLevel.ERROR, SeverityLevel.CRITICAL],
                start_at=datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0),
                end_at=datetime.now(timezone.utc),
            )
            error_rate = (last_day_errors / last_day_total * 100) if last_day_total else 0.0
            health_score = max(20.0, round(100.0 - (error_rate * 1.5) - open_incidents * 10 - open_alerts * 4, 1))
            service_cards.append(
                ServiceRead.model_validate(service).model_copy(
                    update={
                        "health_score": health_score,
                        "open_incidents": int(open_incidents),
                        "open_alerts": int(open_alerts),
                    }
                )
            )

        mttr = await self.incidents.average_mttr_hours()
        open_incidents = await self.incidents.open_count()
        open_alerts = await self.alerts.open_count()
        total_errors = 0
        total_logs = 0
        for service in services:
            total_errors += await self.logs.count_by_severity(
                service_id=service.id,
                severities=[SeverityLevel.ERROR, SeverityLevel.CRITICAL],
                start_at=datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0),
                end_at=datetime.now(timezone.utc),
            )
            total_logs += await self.logs.count_total(
                service_id=service.id,
                start_at=datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0),
                end_at=datetime.now(timezone.utc),
            )
        error_rate = round((total_errors / total_logs) * 100, 2) if total_logs else 0.0
        avg_health = round(sum(service.health_score for service in service_cards) / len(service_cards), 1) if service_cards else 100.0

        incident_trend = await self._incident_trend()
        error_rate_trend = await self._error_rate_trend()
        alert_volume = [TimeSeriesPoint(timestamp=timestamp, value=float(value)) for timestamp, value in await self.alerts.volume_by_hour()]

        recent_incidents = await self.incidents.list_filtered(limit=8)
        active_alerts = await self.alerts.list_alerts(limit=8)

        return DashboardOverview(
            metrics=[
                MetricCard(label="Open incidents", value=float(open_incidents), delta=8.0),
                MetricCard(label="MTTR", value=mttr, delta=-12.0, suffix="h"),
                MetricCard(label="Error rate", value=error_rate, delta=2.6, suffix="%"),
                MetricCard(label="Service health", value=avg_health, delta=1.8, suffix="%"),
                MetricCard(label="Open alerts", value=float(open_alerts), delta=4.0),
            ],
            incident_trend=incident_trend,
            error_rate_trend=error_rate_trend,
            alert_volume_trend=alert_volume,
            services=service_cards,
            recent_incidents=[item for item in recent_incidents],
            active_alerts=[item for item in active_alerts if item.status.value != "resolved"],
        )

    async def _incident_trend(self) -> list[TimeSeriesPoint]:
        points = [TimeSeriesPoint(timestamp=timestamp, value=float(value)) for timestamp, value in await self.logs.bucket_by_hour(service_id=None, severity=SeverityLevel.ERROR)]
        return points

    async def _error_rate_trend(self) -> list[TimeSeriesPoint]:
        total_points = defaultdict(float)
        error_points = defaultdict(float)

        for timestamp, count in await self.logs.bucket_by_hour(service_id=None):
            total_points[timestamp] = float(count)
        for timestamp, count in await self.logs.bucket_by_hour(service_id=None, severity=SeverityLevel.ERROR):
            error_points[timestamp] += float(count)
        for timestamp, count in await self.logs.bucket_by_hour(service_id=None, severity=SeverityLevel.CRITICAL):
            error_points[timestamp] += float(count)

        series = []
        for timestamp in sorted(total_points):
            total = total_points[timestamp]
            errors = error_points[timestamp]
            rate = (errors / total * 100) if total else 0.0
            series.append(TimeSeriesPoint(timestamp=timestamp, value=round(rate, 2)))
        return series
