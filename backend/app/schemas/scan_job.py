"""ScanJob Pydantic schemas."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.scan_job import ScanJobStatus, ScanType


class ScanJobCreate(BaseModel):
    """Schema for triggering a new repository analysis scan job."""

    repository_id: uuid.UUID = Field(..., description="Target repository identifier to analyze")
    scan_type: ScanType = Field(default=ScanType.FULL, description="Target analysis scan type")


class ScanJobUpdate(BaseModel):
    """Schema for updating scan job progress and status."""

    status: Optional[ScanJobStatus] = Field(None, description="Updated lifecycle status")
    progress: Optional[int] = Field(None, ge=0, le=100, description="Completion percentage from 0 to 100")
    error_message: Optional[str] = Field(None, description="Detailed failure reason if status is FAILED")


class ScanJobResponse(BaseModel):
    """Scan job status response model."""

    id: uuid.UUID
    repository_id: uuid.UUID
    status: str
    scan_type: str
    progress: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScanJobFilter(BaseModel):
    """Query filter parameters for scan jobs."""

    repository_id: Optional[uuid.UUID] = None
    status: Optional[ScanJobStatus] = None
    scan_type: Optional[ScanType] = None
