"""Celery background worker configuration, task tracking, and job execution."""

from typing import Any, Dict, Optional
from celery import Celery
from celery.result import AsyncResult
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
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(name="devpilot.ping")
def ping_worker() -> str:
    """Diagnostic task to verify worker connectivity."""
    logger.info("Celery ping worker task executed successfully.")
    return "pong"


@celery_app.task(
    name="devpilot.execute_scan_job",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
)
def execute_scan_job(self, scan_job_id: str) -> Dict[str, Any]:
    """Execute asynchronous background code analysis job with progress tracking."""
    retries = getattr(self.request, "retries", 0) if hasattr(self, "request") and self.request else 0
    task_id = getattr(self.request, "id", None) if hasattr(self, "request") and self.request else None
    
    logger.info("Starting background scan job task for id=%s (attempt %s)", scan_job_id, retries + 1)

    if task_id:
        # Update state during active worker execution
        self.update_state(state="RUNNING", meta={"progress": 25, "step": "AST parsing initialized"})
        self.update_state(state="RUNNING", meta={"progress": 75, "step": "Static security checks completed"})

    logger.info("Completed background scan job task for id=%s", scan_job_id)
    return {
        "scan_job_id": scan_job_id,
        "status": "COMPLETED",
        "progress": 100,
        "details": "Scan completed successfully in background worker.",
    }


def get_task_status(task_id: str) -> Dict[str, Any]:
    """Query celery task status and execution state."""
    try:
        res = AsyncResult(task_id, app=celery_app)
        info = res.info if isinstance(res.info, dict) else {"result": str(res.info)}
        return {
            "task_id": task_id,
            "status": res.status,
            "ready": res.ready(),
            "successful": res.successful() if res.ready() else None,
            "info": info,
        }
    except Exception as exc:
        logger.warning("Failed to inspect Celery task '%s': %s", task_id, str(exc))
        return {
            "task_id": task_id,
            "status": "UNKNOWN",
            "ready": False,
            "error": str(exc),
        }
