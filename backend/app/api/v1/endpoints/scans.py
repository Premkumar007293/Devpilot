"""Scan job management and execution API endpoints."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.exceptions import ResourceNotFoundException
from app.database.session import get_db
from app.models.scan_job import ScanJobStatus, ScanType
from app.schemas.common import PaginatedResponse
from app.schemas.scan_job import (
    ScanJobCreate,
    ScanJobFilter,
    ScanJobResponse,
    ScanJobUpdate,
)
from app.services.scan_job_service import ScanJobService

router = APIRouter()


@router.post(
    "",
    response_model=ScanJobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Scan Job Record",
    description="Registers a new code analysis scan job for a repository and queues background execution.",
)
def create_scan_job(
    scan_in: ScanJobCreate,
    dispatch_async: bool = Query(True, description="Whether to dispatch background Celery task"),
    db: Session = Depends(get_db),
) -> ScanJobResponse:
    """Create a scan job record."""
    scan = ScanJobService.create_scan_job(db=db, scan_in=scan_in, dispatch_async=dispatch_async)
    return ScanJobResponse.model_validate(scan)


@router.get(
    "",
    response_model=PaginatedResponse[ScanJobResponse],
    status_code=status.HTTP_200_OK,
    summary="List Scan Jobs",
    description="Retrieves a paginated list of scan jobs with optional filtering by repository, status, or scan type.",
)
def list_scan_jobs(
    repository_id: Optional[uuid.UUID] = Query(None, description="Filter by repository UUID"),
    status_filter: Optional[ScanJobStatus] = Query(None, alias="status", description="Filter by lifecycle status"),
    scan_type: Optional[ScanType] = Query(None, description="Filter by scan type"),
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Records per page"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[ScanJobResponse]:
    """List scan jobs with filtering and pagination."""
    filter_params = ScanJobFilter(
        repository_id=repository_id,
        status=status_filter,
        scan_type=scan_type,
    )
    items, total = ScanJobService.list_scan_jobs(
        db=db, filter_params=filter_params, skip=skip, limit=limit
    )
    return PaginatedResponse[ScanJobResponse](
        items=[ScanJobResponse.model_validate(item) for item in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{scan_id}",
    response_model=ScanJobResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Scan Job Details",
    description="Fetches scan progress, execution status, and findings by scan UUID.",
)
def get_scan_job(
    scan_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> ScanJobResponse:
    """Get scan job by UUID."""
    scan = ScanJobService.get_scan_job_by_id(db=db, scan_id=scan_id)
    if not scan:
        raise ResourceNotFoundException("ScanJob", scan_id)
    return ScanJobResponse.model_validate(scan)


@router.patch(
    "/{scan_id}",
    response_model=ScanJobResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Scan Status and Progress",
    description="Updates scan progress percentage, lifecycle state, or error details.",
)
def update_scan_job(
    scan_id: uuid.UUID,
    scan_update: ScanJobUpdate,
    db: Session = Depends(get_db),
) -> ScanJobResponse:
    """Update scan job progress and status."""
    scan = ScanJobService.get_scan_job_by_id(db=db, scan_id=scan_id)
    if not scan:
        raise ResourceNotFoundException("ScanJob", scan_id)
    updated = ScanJobService.update_scan_job(db=db, scan=scan, update_in=scan_update)
    return ScanJobResponse.model_validate(updated)


@router.post(
    "/{scan_id}/cancel",
    response_model=ScanJobResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel Scan Job",
    description="Terminates a queued or in-progress scan job and marks status as CANCELLED.",
)
def cancel_scan_job(
    scan_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> ScanJobResponse:
    """Cancel scan job by UUID."""
    scan = ScanJobService.get_scan_job_by_id(db=db, scan_id=scan_id)
    if not scan:
        raise ResourceNotFoundException("ScanJob", scan_id)
    cancelled = ScanJobService.cancel_scan_job(db=db, scan=scan)
    return ScanJobResponse.model_validate(cancelled)
