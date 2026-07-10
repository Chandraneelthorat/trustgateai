"""Celery singleton (isolates decorator imports from worker bootstrap)."""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "trustgateai",
    broker=settings.broker_url,
    backend=settings.result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

import app.tasks  # noqa: E402,F401  # Registers tasks on Celery singleton
