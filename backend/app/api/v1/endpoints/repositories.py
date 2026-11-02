"""Repository management API endpoints."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.exceptions import ResourceNotFoundException
from app.database.session import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.repository import (
    RepositoryCreate,
    RepositoryFilter,
    RepositoryResponse,
    RepositoryUpdate,
)
from app.services.repository_service import RepositoryService

router = APIRouter()


@router.post(
    "",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Repository Record",
    description="Registers a new repository metadata record under an organization.",
)
def create_repository(
    repo_in: RepositoryCreate,
    db: Session = Depends(get_db),
) -> RepositoryResponse:
    """Create a new repository record."""
    repo = RepositoryService.create_repository(db=db, repo_in=repo_in)
    return RepositoryResponse.model_validate(repo)


@router.get(
    "",
    response_model=PaginatedResponse[RepositoryResponse],
    status_code=status.HTTP_200_OK,
    summary="List Repositories",
    description="Retrieves a paginated list of repositories with optional filtering.",
)
def list_repositories(
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter by organization UUID"),
    provider: Optional[str] = Query(None, description="Filter by provider (e.g. github)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_private: Optional[bool] = Query(None, description="Filter by private/public visibility"),
    search: Optional[str] = Query(None, description="Search repository name or description"),
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Records per page"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[RepositoryResponse]:
    """List repositories with filtering and pagination."""
    filter_params = RepositoryFilter(
        organization_id=organization_id,
        provider=provider,
        is_active=is_active,
        is_private=is_private,
        search=search,
    )
    items, total = RepositoryService.list_repositories(
        db=db, filter_params=filter_params, skip=skip, limit=limit
    )
    return PaginatedResponse[RepositoryResponse](
        items=[RepositoryResponse.model_validate(item) for item in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{repo_id}",
    response_model=RepositoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Repository Details",
    description="Fetches detailed repository information by its UUID identifier.",
)
def get_repository(
    repo_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> RepositoryResponse:
    """Get repository by UUID."""
    repo = RepositoryService.get_repository_by_id(db=db, repo_id=repo_id)
    if not repo:
        raise ResourceNotFoundException("Repository", repo_id)
    return RepositoryResponse.model_validate(repo)


@router.patch(
    "/{repo_id}",
    response_model=RepositoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Repository Metadata",
    description="Modifies repository metadata, description, default branch, or active status.",
)
def update_repository(
    repo_id: uuid.UUID,
    repo_update: RepositoryUpdate,
    db: Session = Depends(get_db),
) -> RepositoryResponse:
    """Update repository metadata."""
    repo = RepositoryService.get_repository_by_id(db=db, repo_id=repo_id)
    if not repo:
        raise ResourceNotFoundException("Repository", repo_id)
    updated = RepositoryService.update_repository(db=db, repo=repo, update_in=repo_update)
    return RepositoryResponse.model_validate(updated)


@router.delete(
    "/{repo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Repository Record",
    description="Permanently removes a repository and cascades deletion to scan jobs.",
)
def delete_repository(
    repo_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    """Delete repository by UUID."""
    repo = RepositoryService.get_repository_by_id(db=db, repo_id=repo_id)
    if not repo:
        raise ResourceNotFoundException("Repository", repo_id)
    RepositoryService.delete_repository(db=db, repo=repo)
