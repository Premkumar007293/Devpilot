"""Repository-grounded RAG QA endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.exceptions import ResourceNotFoundException
from app.database.session import get_db
from app.models.repository import Repository
from app.models.repository_file import RepositoryFile
from app.models.user import User
from app.rag.pipeline import RepoRAGPipeline
from app.services.repository_service import RepositoryService

router = APIRouter()


@router.post(
    "/ask",
    status_code=status.HTTP_200_OK,
    summary="Ask the repository RAG brain",
    description="Ask a repository-grounded question using the local retrieval pipeline.",
)
def ask_repository_rag(
    repo_id: uuid.UUID = Query(..., description="Repository identifier"),
    question: str = Query(..., min_length=1, description="Question to answer using repository context"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Answer a repository question with file-grounded retrieval evidence."""
    repo = RepositoryService.get_repository_by_id(db=db, repo_id=repo_id)
    if not repo:
        raise ResourceNotFoundException("Repository", repo_id)
    if not RepositoryService.check_user_access(db, repo, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to this repository.")

    repo_files = db.scalars(
        select(RepositoryFile).where(RepositoryFile.repository_id == repo.id).order_by(RepositoryFile.path.asc())
    ).all()
    payloads = [
        {"id": str(file.id), "path": file.path, "content": file.content or ""}
        for file in repo_files
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
