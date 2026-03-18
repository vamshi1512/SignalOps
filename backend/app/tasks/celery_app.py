from __future__ import annotations

from celery import Celery

from app.core.config import get_settings


settings = get_settings()

celery_app = Celery(
    "signalops",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    timezone="UTC",
    beat_schedule={
        "demo-tick": {
            "task": "app.tasks.jobs.demo_tick",
            "schedule": 30.0,
        },
        "alert-escalation-check": {
            "task": "app.tasks.jobs.process_escalations",
            "schedule": 60.0,
        },
    },
)

