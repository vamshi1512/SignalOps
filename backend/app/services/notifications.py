from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import NotificationChannel, NotificationStatus
from app.models.qa import NotificationEvent, TestRun
from app.services.serializers import serialize_notification


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_notifications(self, limit: int = 25) -> list[dict]:
        result = await self.session.execute(
            select(NotificationEvent)
            .order_by(NotificationEvent.created_at.desc())
            .limit(limit)
        )
        return [serialize_notification(item) for item in result.scalars().all()]

    async def notify_failed_run(self, run: TestRun) -> list[NotificationEvent]:
        failing_modules = sorted({result.module_name for result in run.results if result.error_message})
        module_fragment = ", ".join(failing_modules[:3]) if failing_modules else run.suite.name
        delivered_at = run.finished_at or datetime.now(timezone.utc)
        notifications = [
            NotificationEvent(
                run_id=run.id,
                channel=NotificationChannel.SLACK,
                status=NotificationStatus.SENT,
                recipient="#qa-alerts",
                subject=f"Failed run: {run.suite.name}",
                message=f"{run.suite.name} failed in {run.environment.name}. Modules: {module_fragment}.",
                delivered_at=delivered_at,
                payload={"severity": "warning", "fail_count": run.fail_count},
            ),
            NotificationEvent(
                run_id=run.id,
                channel=NotificationChannel.EMAIL,
                status=NotificationStatus.SENT,
                recipient="qa-oncall@testforge.dev",
                subject=f"[TestForge] Failure in {run.suite.name}",
                message=f"Run {run.id} ended with {run.fail_count} failing results and {run.flaky_count} flaky indicators.",
                delivered_at=delivered_at,
                payload={"environment": run.environment.slug, "suite_slug": run.suite.slug},
            ),
        ]
        self.session.add_all(notifications)
        await self.session.flush()
        return notifications

    async def get_notifications_for_run(self, run_id: str) -> list[NotificationEvent]:
        result = await self.session.execute(
            select(NotificationEvent)
            .where(NotificationEvent.run_id == run_id)
            .options(selectinload(NotificationEvent.run))
            .order_by(NotificationEvent.created_at)
        )
        return list(result.scalars().all())
