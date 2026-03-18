from __future__ import annotations

import asyncio

from app.db.session import get_session_factory
from app.services.alerts import AlertService
from app.services.demo import DemoService
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.jobs.demo_tick")
def demo_tick() -> int:
    async def _run() -> int:
        async with get_session_factory()() as session:
            service = DemoService(session)
            return await service.generate_tick()

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.jobs.process_escalations")
def process_escalations() -> int:
    async def _run() -> int:
        async with get_session_factory()() as session:
            service = AlertService(session)
            return await service.process_escalations()

    return asyncio.run(_run())

