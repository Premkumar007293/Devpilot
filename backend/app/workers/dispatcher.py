"""Unified background task dispatcher supporting Celery and local thread pool execution."""

import concurrent.futures
from typing import Any, Dict
from app.core.config import settings
from app.core.logging import logger
from app.workers.celery_app import execute_scan_job, process_scan_job

_local_executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=4, thread_name_prefix="devpilot-worker"
)


def is_celery_available() -> bool:
    """Check if Redis broker is reachable for Celery dispatch."""
    try:
        import redis
        broker_url = settings.CELERY_BROKER_URL or settings.REDIS_URL
        r = redis.from_url(broker_url, socket_timeout=0.5)
        return bool(r.ping())
    except Exception:
        return False


def dispatch_scan_job(scan_job_id: str) -> str:
    """Dispatch scan job to Celery if available, otherwise run in local background thread.

    Returns:
        str: Dispatch mode ("celery" or "local")
    """
    if is_celery_available():
        try:
            execute_scan_job.delay(scan_job_id)
            logger.info("Dispatched scan job id=%s via Celery worker", scan_job_id)
            return "celery"
        except Exception as exc:
            logger.warning("Celery dispatch failed (%s), falling back to local executor", exc)

    # Local fallback execution via non-blocking ThreadPoolExecutor
    _local_executor.submit(process_scan_job, scan_job_id)
    logger.info("Dispatched scan job id=%s via local background executor", scan_job_id)
    return "local"
