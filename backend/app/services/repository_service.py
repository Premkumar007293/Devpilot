"""Repository service handling repository management and queries."""

import uuid
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.exceptions import DevPilotException, ResourceNotFoundException
from app.core.logging import logger
from app.models.organization import Organization
from app.models.repository import Repository
from app.schemas.repository import RepositoryCreate, RepositoryFilter, RepositoryUpdate


class RepositoryService:
    """Service encapsulating repository lifecycle operations."""

    @staticmethod
    def create_repository(db: Session, repo_in: RepositoryCreate) -> Repository:
        """Create a new repository under an organization."""
        org = db.scalar(select(Organization).where(Organization.id == repo_in.organization_id))
        if not org:
            raise ResourceNotFoundException("Organization", repo_in.organization_id)

        full_name = repo_in.full_name or f"{org.slug}/{repo_in.name}"

        # Check existing repo in org
        existing = db.scalar(
            select(Repository).where(
                Repository.organization_id == repo_in.organization_id,
                Repository.name == repo_in.name,
            )
        )
        if existing:
            raise DevPilotException(
                message=f"Repository '{repo_in.name}' already exists in this organization.",
                status_code=409,
            )

        repo = Repository(
            organization_id=repo_in.organization_id,
            name=repo_in.name,
            full_name=full_name,
            description=repo_in.description or "",
            provider=repo_in.provider,
            external_id=repo_in.external_id,
            html_url=repo_in.html_url,
            default_branch=repo_in.default_branch,
            is_private=repo_in.is_private,
            is_active=repo_in.is_active,
        )
        db.add(repo)
        try:
            db.commit()
            db.refresh(repo)
            logger.info("Created repository id=%s full_name=%s", repo.id, repo.full_name)
            return repo
        except IntegrityError as exc:
            db.rollback()
            logger.warning("Repository creation conflict: %s", str(exc))
            raise DevPilotException(
                message=f"Repository '{repo_in.name}' already exists in this organization.",
                status_code=409,
            )

    @staticmethod
    def list_repositories(
        db: Session, filter_params: RepositoryFilter, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Repository], int]:
        """List repositories matching filter criteria with pagination."""
        conditions = []

        if filter_params.organization_id:
            conditions.append(Repository.organization_id == filter_params.organization_id)
        if filter_params.provider:
            conditions.append(Repository.provider == filter_params.provider)
        if filter_params.is_active is not None:
            conditions.append(Repository.is_active == filter_params.is_active)
        if filter_params.is_private is not None:
            conditions.append(Repository.is_private == filter_params.is_private)
        if filter_params.search:
            pattern = f"%{filter_params.search}%"
            conditions.append(Repository.name.ilike(pattern) | Repository.description.ilike(pattern))

        count_query = select(func.count()).select_from(Repository)
        if conditions:
            count_query = count_query.where(*conditions)
        total = db.scalar(count_query) or 0

        query = select(Repository)
        if conditions:
            query = query.where(*conditions)
        query = query.offset(skip).limit(limit).order_by(Repository.created_at.desc())
        items = list(db.scalars(query).all())

        return items, total

    @staticmethod
    def get_repository_by_id(db: Session, repo_id: uuid.UUID) -> Optional[Repository]:
        """Fetch repository by primary UUID."""
        return db.scalar(select(Repository).where(Repository.id == repo_id))

    @staticmethod
    def update_repository(
        db: Session, repo: Repository, update_in: RepositoryUpdate
    ) -> Repository:
        """Update repository metadata and active status."""
        update_data = update_in.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(repo, key, value)

        db.commit()
        db.refresh(repo)
        logger.info("Updated repository id=%s", repo.id)
        return repo

    @staticmethod
    def delete_repository(db: Session, repo: Repository) -> None:
        """Delete repository and cascade to scan jobs."""
        repo_id = repo.id
        db.delete(repo)
        db.commit()
        logger.info("Deleted repository id=%s", repo_id)
