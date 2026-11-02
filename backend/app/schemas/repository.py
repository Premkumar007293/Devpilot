"""Repository Pydantic schemas."""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class RepositoryBase(BaseModel):
    """Base repository properties."""

    name: str = Field(..., min_length=1, max_length=255, description="Repository name", json_schema_extra={"example": "devpilot-core"})
    full_name: Optional[str] = Field(None, max_length=512, description="Full repository path", json_schema_extra={"example": "acme/devpilot-core"})
    description: Optional[str] = Field(None, description="Repository description")
    provider: str = Field("github", max_length=64, description="VCS provider (e.g. github, gitlab, bitbucket)", json_schema_extra={"example": "github"})
    external_id: Optional[str] = Field(None, max_length=255, description="External provider repository ID")
    html_url: Optional[str] = Field(None, max_length=1024, description="Web URL of the repository")
    default_branch: str = Field("main", max_length=128, description="Default git branch")
    is_private: bool = Field(False, description="Whether the repository is private")
    is_active: bool = Field(True, description="Whether the repository is currently active and monitored")


class RepositoryCreate(RepositoryBase):
    """Schema for registering a repository under an organization."""

    organization_id: uuid.UUID = Field(..., description="Parent organization identifier")


class RepositoryUpdate(BaseModel):
    """Schema for updating repository settings and metadata."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    full_name: Optional[str] = Field(None, max_length=512)
    description: Optional[str] = None
    default_branch: Optional[str] = Field(None, max_length=128)
    is_private: Optional[bool] = None
    is_active: Optional[bool] = None
    html_url: Optional[str] = None


class RepositoryResponse(RepositoryBase):
    """Repository response model."""

    id: uuid.UUID
    organization_id: uuid.UUID
    full_name: str
    last_scanned_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RepositoryFilter(BaseModel):
    """Query filter parameters for repository listing."""

    organization_id: Optional[uuid.UUID] = None
    provider: Optional[str] = None
    is_active: Optional[bool] = None
    is_private: Optional[bool] = None
    search: Optional[str] = None
