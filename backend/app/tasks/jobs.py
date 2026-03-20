from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.db.session import get_session_factory
from app.models.mission import Mission
from app.services.alerts import AlertService
from app.services.configuration import ConfigurationService
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.jobs.analytics_rollup")
def analytics_rollup() -> int:
    async def _run() -> int:
        async with get_session_factory()() as session:
            result = await session.execute(select(Mission))
            return len(result.scalars().all())

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.jobs.weather_pulse")
def weather_pulse() -> int:
    async def _run() -> int:
        async with get_session_factory()() as session:
            config = await ConfigurationService(session).get_or_create()
            config.weather_intensity = round((config.weather_intensity + 0.03) % 0.38, 2)
            await session.commit()
            return int(config.weather_intensity * 100)

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.jobs.open_alert_count")
def open_alert_count() -> int:
    async def _run() -> int:
        async with get_session_factory()() as session:
            return await AlertService(session).process_rollup()

    return asyncio.run(_run())
