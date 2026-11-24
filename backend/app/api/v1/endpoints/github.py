"""GitHub integration endpoints for exploring user repositories."""

import hashlib
import hmac
import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, get_optional_current_user
from app.core.config import settings
from app.database.session import get_db
from app.integrations.github.client import GitHubAPIException, GitHubClient
from app.models.organization_member import OrganizationMember
from app.models.repository import Repository
from app.models.user import User
from app.models.webhook_event import WebhookEvent
from app.schemas.auth import OAuthCallbackRequest, OAuthUrlResponse
from app.schemas.repository import GitHubAccessibleRepo, RepositoryConnectRequest, RepositoryResponse
from app.services.github_service import GitHubService
from app.services.repository_service import RepositoryService

router = APIRouter()


def _verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Validate GitHub webhook HMAC-SHA256 signatures."""
    if not secret or not signature:
        return False
    expected = "sha256=" + hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.get(
    "/connect",
    response_model=OAuthUrlResponse,
    status_code=status.HTTP_200_OK,
    summary="Initialize GitHub OAuth connection",
    description="Generates the GitHub authorization URL for the signed-in user or new user session.",
)
def connect_github_account(
    redirect_origin: Optional[str] = Query(None, description="Frontend origin URL for callback redirection"),
    login: Optional[str] = Query(None, description="Suggested GitHub login email or username"),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> OAuthUrlResponse:
    """Generate GitHub OAuth authorization URL for the current app session."""
    url, state = GitHubService.get_login_url(current_user, redirect_origin=redirect_origin, login=login)
    return OAuthUrlResponse(authorization_url=url, state=state)


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Check GitHub connection status",
    description="Returns whether the current user has an active GitHub connection and summary metadata.",
)
async def github_connection_status(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Check whether the current DevPilot user is connected to GitHub."""
    if not current_user or not current_user.github_access_token:
        return {"connected": False, "user": None, "repository_count": 0}

    try:
        profile = await GitHubClient(token=current_user.github_access_token).get_user_profile()
        repos = await GitHubService.list_accessible_repositories(db=db, user=current_user)
        return {
            "connected": True,
            "user": {
                "login": profile.get("login"),
                "name": profile.get("name") or profile.get("login"),
                "avatar_url": profile.get("avatar_url"),
                "html_url": profile.get("html_url"),
            },
            "repository_count": len(repos),
            "github_id": profile.get("id"),
        }
    except GitHubAPIException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get(
    "/user",
    status_code=status.HTTP_200_OK,
    summary="Fetch authenticated GitHub user profile",
    description="Retrieves the GitHub profile for the current DevPilot user.",
)
async def github_user_profile(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Return the current connected GitHub user's profile."""
    return await GitHubService.get_authenticated_user_profile(current_user)


@router.get(
    "/repositories",
    response_model=List[GitHubAccessibleRepo],
    status_code=status.HTTP_200_OK,
    summary="List Accessible GitHub Repositories",
    description="Retrieves public and private repositories accessible by the signed-in user's GitHub account.",
)
async def list_github_repositories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[GitHubAccessibleRepo]:
    """Fetch GitHub repositories accessible to authenticated user."""
    items = await GitHubService.list_accessible_repositories(db=db, user=current_user)
    return [GitHubAccessibleRepo(**item) for item in items]


@router.get(
    "/repositories/{owner}/{repo}",
    status_code=status.HTTP_200_OK,
    summary="Get GitHub repository details",
    description="Fetches details for a single repository using the current user's GitHub token.",
)
async def get_repository_details(
    owner: str,
    repo: str,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Return details for a GitHub repository accessible to the current user."""
    if not owner or not repo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Repository owner and name are required.")
    return await GitHubService.get_repository_details(owner=owner, repo=repo, user=current_user)


@router.delete(
    "/disconnect",
    status_code=status.HTTP_200_OK,
    summary="Disconnect GitHub account",
    description="Removes the current user's GitHub OAuth connection and associated access token.",
)
def disconnect_github_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Securely disconnect the active GitHub OAuth account."""
    GitHubService.disconnect_github_account(db=db, user=current_user)
    return {"status": "disconnected", "message": "GitHub account disconnected successfully."}


@router.get(
    "/callback",
    summary="Complete GitHub OAuth callback",
    description="Processes the GitHub authorization code, validates state, and redirects the browser back to the app with a JWT token.",
)
async def github_oauth_callback(
    code: str = Query(..., description="GitHub authorization code"),
    state: str = Query(..., description="OAuth CSRF state token"),
    db: Session = Depends(get_db),
):
    """Handle the GitHub OAuth callback and redirect the browser with a DevPilot JWT token."""
    if not code or not state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="GitHub OAuth callback is missing required parameters.")

    user, token, origin = await GitHubService.authenticate_github_user(db=db, code=code, state=state)
    target_base = origin if origin else (settings.GITHUB_REDIRECT_URI or "http://localhost:5173/auth/callback")
    if not target_base.endswith("/auth/callback"):
        target_base = f"{target_base.rstrip('/')}/auth/callback"
    separator = "&" if "?" in target_base else "?"
    redirect_target = f"{target_base}{separator}token={token}"
    return RedirectResponse(url=redirect_target)


@router.post(
    "/repositories/connect",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Connect a GitHub Repository to DevPilot",
    description="Connect an accessible GitHub repository using the authenticated user's GitHub permissions.",
)
def connect_repository(
    request: RepositoryConnectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RepositoryResponse:
    """Connect a GitHub repository to DevPilot under an organization."""
    repo = RepositoryService.connect_github_repository(
        db=db,
        user=current_user,
        github_repo_id=request.github_repo_id,
        organization_id=request.organization_id,
    )
    return RepositoryResponse.model_validate(repo)


@router.get(
    "/repositories/connected",
    response_model=List[RepositoryResponse],
    status_code=status.HTTP_200_OK,
    summary="List Connected Repositories",
    description="Returns repositories connected to the authenticated user or their organizations.",
)
def list_connected_repositories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[RepositoryResponse]:
    """List repositories visible to the current user."""
    org_ids = db.scalars(
        select(OrganizationMember.organization_id).where(OrganizationMember.user_id == current_user.id)
    ).all()
    repos = db.scalars(
        select(Repository)
        .where(
            Repository.is_active == True,
            ((Repository.owner_user_id == current_user.id) | (Repository.organization_id.in_(org_ids)))
        )
        .order_by(Repository.created_at.desc())
    ).all()
    return [RepositoryResponse.model_validate(repo) for repo in repos]


@router.post(
    "/webhook",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive GitHub Webhook Events",
    description="Accepts GitHub webhook deliveries after verifying the SHA-256 HMAC signature.",
)
async def github_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Process GitHub webhook events with duplicate delivery protection."""
    payload = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    event_type = request.headers.get("X-GitHub-Event", "")
    delivery_id = request.headers.get("X-GitHub-Delivery", "")

    if not event_type or not delivery_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing GitHub webhook headers.")

    secret = settings.GITHUB_WEBHOOK_SECRET
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub webhook secret is not configured.",
        )

    if not _verify_webhook_signature(payload, signature, secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature.")

    existing = db.scalar(select(WebhookEvent).where(WebhookEvent.delivery_id == delivery_id))
    if existing:
        return {"status": "duplicate", "event_type": event_type, "delivery_id": delivery_id}

    try:
        body = json.loads(payload.decode("utf-8")) if payload else {}
    except json.JSONDecodeError:
        body = {}

    repo_name = None
    if isinstance(body, dict):
        repo = body.get("repository") or {}
        repo_name = repo.get("full_name") or repo.get("name")

    event = WebhookEvent(
        delivery_id=delivery_id,
        event_type=event_type,
        repository_name=repo_name,
        payload_summary=json.dumps({"repository": repo_name, "event": event_type})[:2000],
        processed=True,
    )
    db.add(event)
    db.commit()

    return {"status": "accepted", "event_type": event_type, "delivery_id": delivery_id}

