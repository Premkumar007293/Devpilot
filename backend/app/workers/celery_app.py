"""Celery background worker configuration and task registration."""

from celery import Celery
from app.core.config import settings
from app.core.logging import logger

celery_app = Celery(
    "devpilot_workers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour maximum for heavy repository scans
)


@celery_app.task(name="devpilot.ping")
def ping_worker() -> str:
    """Diagnostic task to verify worker connectivity."""
    logger.info("Celery ping worker task executed successfully.")
    return "pong"
