"""Repository service handling repository management, GitHub connection, and access control."""

import asyncio
import uuid
from typing import Any, Dict, List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.exceptions import DevPilotException, ResourceNotFoundException
from app.core.logging import logger
from app.integrations.github.client import GitHubAPIException, GitHubClient
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.repository import Repository
from app.models.repository_file import RepositoryFile
from app.models.user import User
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
    def check_user_access(db: Session, repo: Repository, user: User) -> bool:
        """Verify whether user owns the repository or belongs to its organization."""
        if repo.owner_user_id == user.id:
            return True

        # Check membership in repository organization
        membership = db.scalar(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == repo.organization_id,
                OrganizationMember.user_id == user.id,
            )
        )
        return membership is not None

    @staticmethod
    def connect_github_repository(
        db: Session,
        user: User,
        github_repo_id: int,
        organization_id: Optional[uuid.UUID] = None,
    ) -> Repository:
        """Connect an accessible GitHub repository to DevPilot under an organization."""
        if not user.github_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User GitHub account is not connected.",
            )

        # 1. Fetch user accessible repositories from GitHub to verify permissions
        gh_client = GitHubClient(token=user.github_access_token)
        loop = asyncio.new_event_loop()
        try:
            accessible_repos = loop.run_until_complete(gh_client.list_user_repositories(per_page=100))
        finally:
            loop.close()

        target_gh_repo = next(
            (r for r in accessible_repos if r.get("id") == github_repo_id),
            None,
        )
        if not target_gh_repo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"GitHub repository with ID {github_repo_id} not found or access denied.",
            )

        # 2. Identify target organization
        org: Optional[Organization] = None
        if organization_id:
            org = db.get(Organization, organization_id)
            if not org or not RepositoryService.check_user_access(
                db, Repository(organization_id=org.id, owner_user_id=user.id), user
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have permission in target organization.",
                )
        else:
            # Default to personal organization
            membership = db.scalar(
                select(OrganizationMember).where(OrganizationMember.user_id == user.id)
            )
            if membership:
                org = db.get(Organization, membership.organization_id)

        if not org:
            # Auto-create workspace organization
            org = Organization(
                name=f"{user.username}'s Workspace",
                slug=f"{user.username.lower()}-workspace",
                description="Auto-generated personal organization workspace",
            )
            db.add(org)
            db.commit()
            db.refresh(org)
            db.add(OrganizationMember(user_id=user.id, organization_id=org.id, role="OWNER"))
            db.commit()

        # 3. Check if repository already exists by external_id
        ext_id = str(target_gh_repo["id"])
        existing = db.scalar(
            select(Repository).where(
                Repository.provider == "github",
                Repository.external_id == ext_id,
            )
        )

        if existing:
            existing.is_active = True
            existing.owner_user_id = user.id
            existing.name = target_gh_repo.get("name", existing.name)
            existing.full_name = target_gh_repo.get("full_name", existing.full_name)
            existing.description = target_gh_repo.get("description") or ""
            existing.html_url = target_gh_repo.get("html_url")
            existing.default_branch = target_gh_repo.get("default_branch") or "main"
            existing.is_private = bool(target_gh_repo.get("private"))
            existing.language = target_gh_repo.get("language") or "Other"
            existing.stars_count = target_gh_repo.get("stargazers_count", 0)
            db.commit()
            db.refresh(existing)
            logger.info("Re-connected existing repository id=%s full_name=%s", existing.id, existing.full_name)
            return existing

        # 4. Create new repository entity
        repo = Repository(
            organization_id=org.id,
            owner_user_id=user.id,
            name=target_gh_repo.get("name"),
            full_name=target_gh_repo.get("full_name"),
            description=target_gh_repo.get("description") or "",
            provider="github",
            external_id=ext_id,
            html_url=target_gh_repo.get("html_url"),
            default_branch=target_gh_repo.get("default_branch") or "main",
            is_private=bool(target_gh_repo.get("private")),
            is_active=True,
            language=target_gh_repo.get("language") or "Other",
            stars_count=target_gh_repo.get("stargazers_count", 0),
            ingestion_status="NOT_INGESTED",
            file_count=0,
            source_file_count=0,
        )
        db.add(repo)
        db.commit()
        db.refresh(repo)
        logger.info("Connected new GitHub repository id=%s full_name=%s", repo.id, repo.full_name)
        return repo

    @staticmethod
    def refresh_repository_metadata(db: Session, repo: Repository, user: User) -> Repository:
        """Refresh repository metadata directly from GitHub API."""
        if not RepositoryService.check_user_access(db, repo, user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this repository.")

        if not user.github_access_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="GitHub access token required.")

        parts = repo.full_name.split("/")
        if len(parts) != 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid full_name format.")

        owner, repo_name = parts[0], parts[1]
        gh_client = GitHubClient(token=user.github_access_token)
        loop = asyncio.new_event_loop()
        try:
            data = loop.run_until_complete(gh_client.get_repository_details(owner=owner, repo=repo_name))
        finally:
            loop.close()

        repo.description = data.get("description") or ""
        repo.default_branch = data.get("default_branch") or repo.default_branch
        repo.language = data.get("language") or repo.language
        repo.stars_count = data.get("stargazers_count", repo.stars_count)
        repo.is_private = bool(data.get("private"))
        db.commit()
        db.refresh(repo)
        logger.info("Refreshed metadata for repository id=%s", repo.id)
        return repo

    @staticmethod
    def disconnect_repository(db: Session, repo: Repository, user: User) -> None:
        """Disconnect repository from platform monitoring."""
        if not RepositoryService.check_user_access(db, repo, user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this repository.")

        repo.is_active = False
        db.commit()
        logger.info("Disconnected repository id=%s (%s)", repo.id, repo.full_name)

    @staticmethod
    def get_repository_files(
        db: Session, repo: Repository, user: User
    ) -> Tuple[List[RepositoryFile], int, int]:
        """Retrieve ingested files and metrics for repository."""
        if not RepositoryService.check_user_access(db, repo, user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this repository.")

        files = db.scalars(
            select(RepositoryFile)
            .where(RepositoryFile.repository_id == repo.id)
            .order_by(RepositoryFile.path.asc())
        ).all()
        file_list = list(files)
        source_count = sum(1 for f in file_list if f.file_type == "source")
        return file_list, len(file_list), source_count

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
