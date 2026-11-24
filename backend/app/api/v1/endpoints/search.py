"""Global search across repositories and indexed source artifacts."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database.session import get_db
from app.models.organization_member import OrganizationMember
from app.models.repository import Repository
from app.models.repository_file import RepositoryFile
from app.models.user import User

router = APIRouter()


@router.get(
    "",
    summary="Global repository search",
    description="Search repositories and ingested files a user is authorized to access.",
)
def global_search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, list[dict[str, Any]]]:
    user_org_ids = db.scalars(
        select(OrganizationMember.organization_id).where(OrganizationMember.user_id == current_user.id)
    ).all()

    repo_query = select(Repository).where(Repository.owner_user_id == current_user.id)
    if user_org_ids:
        repo_query = select(Repository).where(
            or_(
                Repository.owner_user_id == current_user.id,
                Repository.organization_id.in_(user_org_ids),
            )
        )
    repos = db.scalars(repo_query).all()
    normalized_query = q.lower().strip()

    matching_repos = []
    for repo in repos:
        haystack = f"{repo.name} {repo.full_name} {repo.description or ''}".lower()
        if normalized_query in haystack:
            matching_repos.append({
                "id": str(repo.id),
                "name": repo.name,
                "full_name": repo.full_name,
                "language": repo.language or "Unknown",
                "repository_id": str(repo.id),
                "kind": "repository",
            })

    accessible_repo_ids = [repo.id for repo in repos]
    file_query = select(RepositoryFile).where(RepositoryFile.repository_id.in_([repo_id for repo_id in accessible_repo_ids]))
    files = db.scalars(file_query).all()
    matching_files = []
    for file in files:
        haystack = f"{file.path} {file.name}".lower()
        if normalized_query in haystack:
            matching_files.append({
                "id": str(file.id),
                "name": file.name,
                "path": file.path,
                "repository_id": str(file.repository_id),
                "kind": "file",
            })

    return {
        "repositories": matching_repos[:limit],
        "files": matching_files[:limit],
        "total": len(matching_repos) + len(matching_files),
    }
