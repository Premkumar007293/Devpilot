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
    owner_user_id: Optional[uuid.UUID] = None
    full_name: str
    language: Optional[str] = "Other"
    stars_count: int = 0
    last_scanned_at: Optional[datetime] = None
    last_ingested_at: Optional[datetime] = None
    ingestion_status: str = "NOT_INGESTED"
    file_count: int = 0
    source_file_count: int = 0
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


class RepositoryConnectRequest(BaseModel):
    """Payload to connect an accessible GitHub repository."""
    github_repo_id: int = Field(..., description="GitHub external repository ID")
    organization_id: Optional[uuid.UUID] = Field(None, description="Target organization UUID. Defaults to user personal org.")


class GitHubAccessibleRepo(BaseModel):
    """Accessible GitHub repository information."""
    id: int
    name: str
    full_name: str
    description: Optional[str] = ""
    html_url: Optional[str] = None
    default_branch: str = "main"
    is_private: bool = False
    language: Optional[str] = "Other"
    stars_count: int = 0
    is_connected: bool = False
    connected_repository_id: Optional[str] = None


class RepositoryTreeItem(BaseModel):
    """Ingested file entry inside the repository tree."""
    id: uuid.UUID
    path: str
    name: str
    extension: str
    size_bytes: int
    file_type: str
    blob_sha: Optional[str] = None
    is_binary: bool = False
    last_ingested_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RepositoryTreeResponse(BaseModel):
    """Repository file tree structure."""
    repository_id: uuid.UUID
    branch: str
    total_files: int
    source_files: int
    files: List[RepositoryTreeItem]


class RepositoryIngestionJobResponse(BaseModel):
    """Repository ingestion job execution summary."""
    id: uuid.UUID
    repository_id: uuid.UUID
    status: str
    branch: str
    commit_sha: Optional[str] = None
    total_files: int
    source_files: int
    ignored_files: int
    total_bytes: int
    progress: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
