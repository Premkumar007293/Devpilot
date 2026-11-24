"""GitHub service managing OAuth synchronization, repository indexing, and user provisioning."""

import uuid
from typing import Any, Dict, List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.core.security import consume_oauth_state, create_access_token, verify_oauth_state
from app.integrations.github.client import GitHubAPIException, GitHubClient
from app.models.organization import Organization
from app.models.organization_member import MemberRole, OrganizationMember
from app.models.repository import Repository
from app.models.user import User


class GitHubService:
    """Service orchestrating GitHub OAuth lifecycle and repository discovery."""

    @staticmethod
    def get_login_url(user: Optional[User] = None, redirect_origin: Optional[str] = None, login: Optional[str] = None) -> Tuple[str, str]:
        """Generate OAuth authorization URL with a cryptographic CSRF state token bound to the current user."""
        from app.core.security import create_oauth_state
        state = create_oauth_state(str(user.id) if user else None, redirect_origin=redirect_origin)
        client = GitHubClient()
        url = client.get_authorization_url(state=state, login=login)
        return url, state

    @staticmethod
    async def get_authenticated_user_profile(user: User) -> Dict[str, Any]:
        """Return the currently authenticated GitHub user profile for the given DevPilot user."""
        if not user.github_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub account is not connected. Please authenticate with GitHub first.",
            )
        client = GitHubClient(token=user.github_access_token)
        try:
            return await client.get_user_profile()
        except GitHubAPIException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @staticmethod
    async def authenticate_github_user(
        db: Session,
        code: str,
        state: str,
    ) -> Tuple[User, str, Optional[str]]:
        """Verify OAuth state, exchange authorization code, and provision/update user record."""
        state_user_id, redirect_origin = consume_oauth_state(state)
        if not verify_oauth_state(state):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OAuth state token. Possible CSRF attempt.",
            )

        user: Optional[User] = None
        if state_user_id:
            try:
                user = db.get(User, uuid.UUID(state_user_id))
            except Exception:
                user = None

        client = GitHubClient()
        try:
            token_data = await client.exchange_code_for_token(code)
        except GitHubAPIException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message)

        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to obtain access token from GitHub.",
            )

        auth_client = GitHubClient(token=access_token)
        try:
            profile = await auth_client.get_user_profile()
        except GitHubAPIException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message)

        github_id = str(profile.get("id"))
        github_login = profile.get("login") or f"gh_{github_id}"
        email = profile.get("email") or f"{github_login}@users.noreply.github.com"
        full_name = profile.get("name") or github_login
        avatar_url = profile.get("avatar_url")

        existing_user = db.scalar(select(User).where(User.github_id == github_id))
        if not existing_user:
            existing_user = db.scalar(select(User).where(User.email == email))

        if existing_user:
            user = existing_user
            user.github_id = github_id
            user.github_access_token = access_token
            if avatar_url:
                user.avatar_url = avatar_url
            if full_name:
                user.full_name = full_name
            db.commit()
            db.refresh(user)
            logger.info("Updated existing GitHub user login for username=%s", user.username)
        else:
            base_username = github_login
            username_candidate = base_username
            counter = 1
            while db.scalar(select(User).where(User.username == username_candidate)):
                username_candidate = f"{base_username}_{counter}"
                counter += 1

            user = User(
                email=email,
                username=username_candidate,
                full_name=full_name,
                avatar_url=avatar_url,
                github_id=github_id,
                github_access_token=access_token,
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info("Created new user from GitHub login id=%s username=%s", user.id, user.username)

        existing_membership = db.scalar(
            select(OrganizationMember).where(OrganizationMember.user_id == user.id)
        )
        if not existing_membership:
            slug_base = user.username.lower()
            org_slug = slug_base
            org_counter = 1
            while db.scalar(select(Organization).where(Organization.slug == org_slug)):
                org_slug = f"{slug_base}-{org_counter}"
                org_counter += 1

            org = Organization(
                name=f"{user.username}'s Workspace",
                slug=org_slug,
                description=f"Personal organization workspace for {user.username}",
            )
            db.add(org)
            db.commit()
            db.refresh(org)

            db.add(OrganizationMember(
                user_id=user.id,
                organization_id=org.id,
                role=MemberRole.OWNER.value,
            ))
            db.commit()
            logger.info("Provisioned default personal workspace organization for user %s", user.username)

        jwt_token = create_access_token({"sub": str(user.id), "username": user.username})
        return user, jwt_token, redirect_origin

    @staticmethod
    async def list_accessible_repositories(
        db: Session,
        user: User,
    ) -> List[Dict[str, Any]]:
        """Fetch accessible GitHub repositories and annotate with local connection status."""
        if not user.github_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub account is not connected. Please authenticate with GitHub first.",
            )

        client = GitHubClient(token=user.github_access_token)
        try:
            gh_repos = await client.list_user_repositories(per_page=100)
        except GitHubAPIException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message)

        connected_repos = db.scalars(
            select(Repository).where(
                Repository.provider == "github",
                Repository.is_active == True,
            )
        ).all()
        connected_ext_ids = {r.external_id for r in connected_repos if r.external_id}
        connected_map = {r.external_id: r.id for r in connected_repos if r.external_id}

        annotated: List[Dict[str, Any]] = []
        for r in gh_repos:
            ext_id = str(r.get("id"))
            is_connected = ext_id in connected_ext_ids
            annotated.append({
                "id": r.get("id"),
                "name": r.get("name"),
                "full_name": r.get("full_name"),
                "description": r.get("description") or "",
                "html_url": r.get("html_url"),
                "default_branch": r.get("default_branch") or "main",
                "is_private": bool(r.get("private")),
                "language": r.get("language") or "Other",
                "stars_count": r.get("stargazers_count", 0),
                "is_connected": is_connected,
                "connected_repository_id": str(connected_map[ext_id]) if is_connected else None,
            })

        return annotated

    @staticmethod
    async def get_repository_details(owner: str, repo: str, user: User) -> Dict[str, Any]:
        """Fetch the metadata for a single GitHub repository using the user's token."""
        if not user.github_access_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="GitHub account is not connected.")
        client = GitHubClient(token=user.github_access_token)
        try:
            return await client.get_repository_details(owner, repo)
        except GitHubAPIException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @staticmethod
    async def disconnect_github_account(db: Session, user: User) -> None:
        """Remove the connected GitHub token and identifier from the active user."""
        user.github_id = None
        user.github_access_token = None
        user.avatar_url = user.avatar_url or user.avatar_url
        db.commit()
        logger.info("Disconnected GitHub account for user %s", user.username)

