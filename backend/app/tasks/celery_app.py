from __future__ import annotations

from celery import Celery

from app.core.config import get_settings


settings = get_settings()

celery_app = Celery(
    "testforge",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    timezone="UTC",
    task_always_eager=settings.celery_eager,
    beat_schedule={
        "schedule-due-runs": {
            "task": "app.tasks.jobs.schedule_due_runs_task",
            "schedule": 30.0,
        },
    },
)
