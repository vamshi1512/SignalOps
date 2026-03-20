from __future__ import annotations

from celery import Celery

from app.core.config import get_settings


settings = get_settings()

celery_app = Celery(
    "roboyard_control",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    timezone="UTC",
    beat_schedule={
        "analytics-rollup": {
            "task": "app.tasks.jobs.analytics_rollup",
            "schedule": 300.0,
        },
        "weather-pulse": {
            "task": "app.tasks.jobs.weather_pulse",
            "schedule": 180.0,
        },
    },
)
