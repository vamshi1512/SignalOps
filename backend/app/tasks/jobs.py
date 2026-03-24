from __future__ import annotations

import asyncio

from app.db.session import get_session_factory
from app.services.execution import ExecutionService
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.jobs.execute_run_task")
def execute_run_task(run_id: str) -> str:
    async def _run() -> str:
        async with get_session_factory()() as session:
            service = ExecutionService(session)
            await service.execute_run(run_id)
            await session.commit()
            return run_id

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.jobs.schedule_due_runs_task")
def schedule_due_runs_task() -> int:
    async def _run() -> list[str]:
        async with get_session_factory()() as session:
            service = ExecutionService(session)
            run_ids = await service.schedule_due_runs()
            await session.commit()
            return run_ids

    run_ids = asyncio.run(_run())
    for run_id in run_ids:
        execute_run_task.delay(run_id)
    return len(run_ids)
