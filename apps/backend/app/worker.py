"""Convenience re-export so `celery -A app.worker` finds the Celery singleton."""

from app.celery_app import celery_app

app = celery_app

__all__ = ["celery_app", "app"]
