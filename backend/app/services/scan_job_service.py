"""ScanJob service managing code intelligence scanning lifecycle and background dispatches."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.core.exceptions import DevPilotException, ResourceNotFoundException
from app.core.logging import logger
from app.models.repository import Repository
from app.models.scan_job import ScanJob, ScanJobStatus
from app.schemas.scan_job import ScanJobCreate, ScanJobFilter, ScanJobUpdate


class ScanJobService:
    """Service encapsulating scan job creation, status tracking, and dispatching."""

    @staticmethod
    def create_scan_job(
        db: Session, scan_in: ScanJobCreate, dispatch_async: bool = False
    ) -> ScanJob:
        """Create a scan job record and optionally dispatch Celery task."""
        repo = db.scalar(select(Repository).where(Repository.id == scan_in.repository_id))
        if not repo:
            raise ResourceNotFoundException("Repository", scan_in.repository_id)

        scan_type_val = (
            scan_in.scan_type.value
            if hasattr(scan_in.scan_type, "value")
            else str(scan_in.scan_type)
        )

        scan = ScanJob(
            repository_id=scan_in.repository_id,
            status=ScanJobStatus.PENDING.value,
            scan_type=scan_type_val,
            progress=0,
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)
        logger.info("Created scan job id=%s for repository=%s", scan.id, scan.repository_id)

        # Asynchronous dispatch: Celery if Redis is available, otherwise local thread executor
        if dispatch_async:
            try:
                scan.status = ScanJobStatus.QUEUED.value
                db.commit()
                db.refresh(scan)
                from app.workers.dispatcher import dispatch_scan_job
                mode = dispatch_scan_job(str(scan.id))
                logger.info("Dispatched scan job id=%s using %s executor", scan.id, mode)
            except Exception as exc:
                logger.warning("Background task dispatch error: %s", str(exc))

        return scan

    @staticmethod
    def list_scan_jobs(
        db: Session, filter_params: ScanJobFilter, skip: int = 0, limit: int = 20
    ) -> Tuple[List[ScanJob], int]:
        """List scan jobs matching filter criteria with pagination."""
        conditions = []

        if filter_params.repository_id:
            conditions.append(ScanJob.repository_id == filter_params.repository_id)
        if filter_params.status:
            status_val = (
                filter_params.status.value
                if hasattr(filter_params.status, "value")
                else str(filter_params.status)
            )
            conditions.append(ScanJob.status == status_val)
        if filter_params.scan_type:
            type_val = (
                filter_params.scan_type.value
                if hasattr(filter_params.scan_type, "value")
                else str(filter_params.scan_type)
            )
            conditions.append(ScanJob.scan_type == type_val)

        count_query = select(func.count()).select_from(ScanJob)
        if conditions:
            count_query = count_query.where(*conditions)
        total = db.scalar(count_query) or 0

        query = select(ScanJob)
        if conditions:
            query = query.where(*conditions)
        query = query.offset(skip).limit(limit).order_by(ScanJob.created_at.desc())
        items = list(db.scalars(query).all())

        return items, total

    @staticmethod
    def get_scan_job_by_id(db: Session, scan_id: uuid.UUID) -> Optional[ScanJob]:
        """Fetch scan job by primary UUID."""
        return db.scalar(select(ScanJob).where(ScanJob.id == scan_id))

    @staticmethod
    def update_scan_job(
        db: Session, scan: ScanJob, update_in: ScanJobUpdate
    ) -> ScanJob:
        """Update scan job progress, lifecycle status, or failure error."""
        now = datetime.now(timezone.utc)
        update_data = update_in.model_dump(exclude_unset=True)

        if "status" in update_data and update_data["status"]:
            new_status = (
                update_data["status"].value
                if hasattr(update_data["status"], "value")
                else str(update_data["status"])
            )
            scan.status = new_status

            if new_status == ScanJobStatus.RUNNING.value and not scan.started_at:
                scan.started_at = now
            elif new_status in (
                ScanJobStatus.COMPLETED.value,
                ScanJobStatus.FAILED.value,
                ScanJobStatus.CANCELLED.value,
            ):
                scan.completed_at = now
                if new_status == ScanJobStatus.COMPLETED.value:
                    scan.progress = 100
                    # Update parent repository last_scanned_at
                    repo = db.scalar(
                        select(Repository).where(Repository.id == scan.repository_id)
                    )
                    if repo:
                        repo.last_scanned_at = now

        if "progress" in update_data and update_data["progress"] is not None:
            scan.progress = update_data["progress"]

        if "error_message" in update_data:
            scan.error_message = update_data["error_message"]

        db.commit()
        db.refresh(scan)
        logger.info("Updated scan job id=%s status=%s progress=%s", scan.id, scan.status, scan.progress)
        return scan

    @staticmethod
    def cancel_scan_job(db: Session, scan: ScanJob) -> ScanJob:
        """Cancel an in-progress or queued scan job."""
        if scan.status in (
            ScanJobStatus.COMPLETED.value,
            ScanJobStatus.FAILED.value,
            ScanJobStatus.CANCELLED.value,
        ):
            raise DevPilotException(
                message=f"Cannot cancel scan job that is already '{scan.status}'.",
                status_code=400,
            )

        scan.status = ScanJobStatus.CANCELLED.value
        scan.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(scan)
        logger.info("Cancelled scan job id=%s", scan.id)
        return scan
