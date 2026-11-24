"""Repository management API endpoints."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.architecture.engine import ArchitectureAnalyzer
from app.core.auth import get_current_user
from app.core.exceptions import ResourceNotFoundException
from app.database.session import get_db
from app.models.repository import Repository
from app.models.repository_file import RepositoryFile
from app.models.repository_ingestion_job import RepositoryIngestionJob
from app.models.user import User
from app.rag.pipeline import RepoRAGPipeline
from app.schemas.common import PaginatedResponse
from app.schemas.repository import (
    RepositoryConnectRequest,
    RepositoryCreate,
    RepositoryFilter,
    RepositoryIngestionJobResponse,
    RepositoryResponse,
    RepositoryTreeItem,
    RepositoryUpdate,
)
from app.services.ai_engineering_service import AIEngineeringService
from app.services.ingestion_service import IngestionService
from app.services.repository_service import RepositoryService

router = APIRouter()


@router.post(
    "/connect",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Connect GitHub Repository",
    description="Connects an accessible GitHub repository to DevPilot under an organization.",
)
def connect_repository(
    request: RepositoryConnectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RepositoryResponse:
    """Connect an accessible GitHub repository to the current user's workspace."""
    repo = RepositoryService.connect_github_repository(
        db=db,
        user=current_user,
        github_repo_id=request.github_repo_id,
        organization_id=request.organization_id,
    )
    return RepositoryResponse.model_validate(repo)


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


@router.post(
    "/{repo_id}/refresh",
    response_model=RepositoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Repository Metadata",
    description="Refreshes GitHub repository metadata and permissions for the current user.",
)
def refresh_repository(
    repo_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RepositoryResponse:
    """Refresh metadata for a connected repository."""
    repo = RepositoryService.get_repository_by_id(db=db, repo_id=repo_id)
    if not repo:
        raise ResourceNotFoundException("Repository", repo_id)
    refreshed = RepositoryService.refresh_repository_metadata(db=db, repo=repo, user=current_user)
    return RepositoryResponse.model_validate(refreshed)


@router.post(
    "/{repo_id}/disconnect",
    response_model=RepositoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Disconnect Repository",
    description="Disables a connected repository without deleting its metadata record.",
)
def disconnect_repository(
    repo_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RepositoryResponse:
    """Disconnect a repository from active monitoring."""
    repo = RepositoryService.get_repository_by_id(db=db, repo_id=repo_id)
    if not repo:
        raise ResourceNotFoundException("Repository", repo_id)
    RepositoryService.disconnect_repository(db=db, repo=repo, user=current_user)
    return RepositoryResponse.model_validate(repo)


@router.post(
    "/{repo_id}/ingest",
    response_model=RepositoryIngestionJobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start Repository Ingestion",
    description="Starts a repository tree ingestion job and records progress and file metadata.",
)
def start_repository_ingestion(
    repo_id: uuid.UUID,
    branch: Optional[str] = Query(None, description="Branch to ingest"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RepositoryIngestionJobResponse:
    """Start repository ingestion for the current user."""
    repo = RepositoryService.get_repository_by_id(db=db, repo_id=repo_id)
    if not repo:
        raise ResourceNotFoundException("Repository", repo_id)
    job = IngestionService.start_ingestion(
        db=db,
        repository_id=repo.id,
        user=current_user,
        branch=branch,
        dispatch_async=False,
    )
    return RepositoryIngestionJobResponse.model_validate(job)


@router.get(
    "/{repo_id}/ingestion",
    response_model=RepositoryIngestionJobResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Latest Ingestion Status",
    description="Fetches the most recent ingestion job for a repository.",
)
def get_repository_ingestion(
    repo_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> RepositoryIngestionJobResponse:
    """Return the latest ingestion job for a repository."""
    repo = RepositoryService.get_repository_by_id(db=db, repo_id=repo_id)
    if not repo:
        raise ResourceNotFoundException("Repository", repo_id)
    job = db.scalar(
        select(RepositoryIngestionJob)
        .where(RepositoryIngestionJob.repository_id == repo.id)
        .order_by(RepositoryIngestionJob.created_at.desc())
    )
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository has not been ingested yet.")
    return RepositoryIngestionJobResponse.model_validate(job)


@router.get(
    "/{repo_id}/files",
    response_model=list[RepositoryTreeItem],
    status_code=status.HTTP_200_OK,
    summary="List Ingested Repository Files",
    description="Fetches stored file metadata for a repository after ingestion.",
)
def list_repository_files(
    repo_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[RepositoryTreeItem]:
    """Return all ingested repository file metadata ordered by file path."""
    repo = RepositoryService.get_repository_by_id(db=db, repo_id=repo_id)
    if not repo:
        raise ResourceNotFoundException("Repository", repo_id)
    files = db.scalars(
        select(RepositoryFile)
        .where(RepositoryFile.repository_id == repo.id)
        .order_by(RepositoryFile.path.asc())
    ).all()
    return [RepositoryTreeItem.model_validate(file) for file in files]


@router.post(
    "/{repo_id}/ask",
    status_code=status.HTTP_200_OK,
    summary="Ask a repository-grounded question",
    description="Indexes repository file content and answers a question using the local RAG pipeline.",
)
@router.post(
    "/{repo_id}/rag/ask",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def ask_repository_question(
    repo_id: uuid.UUID,
    question: str = Query(..., min_length=1, description="Natural-language question about the repository"),
    top_k: int = Query(default=5, ge=1, le=20),
    similarity_threshold: float = Query(default=0.0, ge=-1.0, le=1.0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Answer repository questions using file-backed context and local retrieval."""
    repo = RepositoryService.get_repository_by_id(db=db, repo_id=repo_id)
    if not repo:
        raise ResourceNotFoundException("Repository", repo_id)
    if not RepositoryService.check_user_access(db, repo, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to this repository.")

    repository_files = db.scalars(
        select(RepositoryFile).where(RepositoryFile.repository_id == repo.id).order_by(RepositoryFile.path.asc())
    ).all()
    payloads = [
        {
            "id": str(file.id),
            "path": file.path,
            "content": file.content or "",
        }
        for file in repository_files
        if file.content
    ]

    pipeline = RepoRAGPipeline()
    if payloads:
        pipeline.index_repository(str(repo.id), payloads)

    return pipeline.ask(
        question,
        str(repo.id),
        repository_name=repo.name,
        repository_full_name=repo.full_name,
        default_branch=repo.default_branch,
    )


@router.get(
    "/{repo_id}/architecture",
    status_code=status.HTTP_200_OK,
    summary="Analyze repository architecture",
    description="Builds the repository dependency graph, layer map, entry points, and cycle analysis from ingested source files.",
)
def analyze_repository_architecture(
    repo_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Return the repository architecture graph and static analysis summary."""
    repo = RepositoryService.get_repository_by_id(db=db, repo_id=repo_id)
    if not repo:
        raise ResourceNotFoundException("Repository", repo_id)
    if not RepositoryService.check_user_access(db, repo, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to this repository.")
    return ArchitectureAnalyzer().analyze_repository(db, repo.id)


@router.get(
    "/{repo_id}/intelligence",
    status_code=status.HTTP_200_OK,
    summary="Analyze repository engineering intelligence",
    description="Builds file-level, module-level, and repository-level understanding using the actual source tree.",
)
def understand_repository_intelligence(
    repo_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Return a structured repository understanding snapshot."""
    repo = RepositoryService.get_repository_by_id(db=db, repo_id=repo_id)
    if not repo:
        raise ResourceNotFoundException("Repository", repo_id)
    if not RepositoryService.check_user_access(db, repo, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to this repository.")
    return AIEngineeringService.understand_repository(db=db, repository_id=repo.id)


@router.post(
    "/{repo_id}/debug",
    status_code=status.HTTP_200_OK,
    summary="Debug a repository issue",
    description="Analyzes a natural-language bug report against the repository context and returns structured investigation guidance.",
)
def debug_repository_issue(
    repo_id: uuid.UUID,
    problem: str = Query(..., min_length=1, description="User-facing description of the bug or problem"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Provide debugging evidence and a suspected root cause for a repository issue."""
    repo = RepositoryService.get_repository_by_id(db=db, repo_id=repo_id)
    if not repo:
        raise ResourceNotFoundException("Repository", repo_id)
    if not RepositoryService.check_user_access(db, repo, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to this repository.")
    return AIEngineeringService.debug_repository_issue(db=db, repository_id=repo.id, problem_description=problem)


@router.get(
    "/{repo_id}/refactors",
    status_code=status.HTTP_200_OK,
    summary="List repository refactoring opportunities",
    description="Constructs a lightweight repository-aware refactoring recommendation list without changing source files.",
)
def recommend_repository_refactors(
    repo_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Return refactoring recommendations derived from the source tree."""
    repo = RepositoryService.get_repository_by_id(db=db, repo_id=repo_id)
    if not repo:
        raise ResourceNotFoundException("Repository", repo_id)
    if not RepositoryService.check_user_access(db, repo, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to this repository.")
    return AIEngineeringService.recommend_refactors(db=db, repository_id=repo.id)


@router.post(
    "/{repo_id}/tests/generate",
    status_code=status.HTTP_200_OK,
    summary="Generate repository-aware test suggestions",
    description="Generates test scaffolds based on repository files and the selected target symbol or function.",
)
def generate_repository_tests(
    repo_id: uuid.UUID,
    target_symbol: Optional[str] = Query(None, description="Optional symbol or behavior to focus the generated tests on"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Generate test suggestions without writing files or executing tests."""
    repo = RepositoryService.get_repository_by_id(db=db, repo_id=repo_id)
    if not repo:
        raise ResourceNotFoundException("Repository", repo_id)
    if not RepositoryService.check_user_access(db, repo, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to this repository.")
    return AIEngineeringService.generate_tests(db=db, repository_id=repo.id, target_symbol=target_symbol)


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
