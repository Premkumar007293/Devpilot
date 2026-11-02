"""Workers package for asynchronous Celery background tasks."""

from app.workers.celery_app import celery_app

__all__ = ["celery_app"]
