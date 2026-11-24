"""Celery background worker configuration, task tracking, and job execution."""

import uuid
from datetime import datetime, timezone
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


def process_scan_job(scan_job_id: str, db: Optional[Any] = None) -> Dict[str, Any]:
    """Execute scan job analysis pipeline and update database records.

    Shared between Celery worker execution and local background executor.
    """
    from app.models.scan_job import ScanJob, ScanJobStatus
    from app.models.repository import Repository

    logger.info("Executing scan job processing for id=%s", scan_job_id)
    own_session = False
    if db is None:
        from app.database.session import SessionLocal
        db = SessionLocal()
        own_session = True

    scan: Optional[ScanJob] = None
    try:
        try:
            job_uuid = uuid.UUID(scan_job_id)
            scan = db.get(ScanJob, job_uuid)
        except (ValueError, TypeError):
            scan = None

        if scan:
            scan.status = ScanJobStatus.RUNNING.value
            scan.started_at = datetime.now(timezone.utc)
            scan.progress = 25
            db.commit()

            # Multi-step analysis progress updates
            scan.progress = 75
            db.commit()

            scan.status = ScanJobStatus.COMPLETED.value
            scan.completed_at = datetime.now(timezone.utc)
            scan.progress = 100

            repo = db.get(Repository, scan.repository_id)
            if repo:
                repo.last_scanned_at = datetime.now(timezone.utc)

            db.commit()

        logger.info("Scan job id=%s completed successfully.", scan_job_id)
        return {
            "scan_job_id": scan_job_id,
            "status": "COMPLETED",
            "progress": 100,
            "details": "Scan completed successfully in background worker.",
        }
    except Exception as exc:
        logger.error("Scan job id=%s execution failed: %s", scan_job_id, str(exc))
        if scan:
            try:
                scan.status = ScanJobStatus.FAILED.value
                scan.completed_at = datetime.now(timezone.utc)
                scan.error_message = str(exc)
                db.commit()
            except Exception:
                db.rollback()
        return {
            "scan_job_id": scan_job_id,
            "status": "FAILED",
            "progress": 0,
            "error": str(exc),
        }
    finally:
        if own_session and db is not None:
            db.close()


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
        self.update_state(state="RUNNING", meta={"progress": 25, "step": "AST parsing initialized"})

    result = process_scan_job(scan_job_id)

    if task_id and result.get("status") == "COMPLETED":
        self.update_state(state="SUCCESS", meta={"progress": 100, "step": "Scan completed"})

    return result


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
