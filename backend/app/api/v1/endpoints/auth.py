"""Authentication endpoints for GitHub OAuth, JWT session management, and current user profile."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.core.config import settings
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import LogoutResponse, OAuthCallbackRequest, OAuthUrlResponse, TokenResponse
from app.schemas.user import UserResponse
from app.services.github_service import GitHubService

router = APIRouter()


@router.get(
    "/github",
    response_model=OAuthUrlResponse,
    status_code=status.HTTP_200_OK,
    summary="Initialize GitHub OAuth Flow",
    description="Generates an OAuth authorization redirect URL and cryptographic CSRF state token.",
)
def get_github_oauth_url(
    redirect_origin: Optional[str] = Query(None, description="Frontend origin URL for callback redirection"),
    login: Optional[str] = Query(None, description="Suggested GitHub login email or username"),
) -> OAuthUrlResponse:
    """Generate GitHub OAuth authorization URL."""
    try:
        url, state = GitHubService.get_login_url(redirect_origin=redirect_origin, login=login)
        return OAuthUrlResponse(authorization_url=url, state=state)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"GitHub OAuth configuration unavailable: {str(exc)}",
        )


@router.post(
    "/github/callback",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Process GitHub OAuth Callback (API)",
    description="Exchanges GitHub authorization code for JWT session token, provisioning user if new.",
)
async def process_github_oauth_callback(
    payload: OAuthCallbackRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Exchange code for user JWT access token."""
    user, token, _ = await GitHubService.authenticate_github_user(
        db=db,
        code=payload.code,
        state=payload.state,
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/github/callback",
    summary="Process GitHub OAuth Redirect (Browser - Legacy Alias)",
    description="Legacy browser redirect handler forwarding to frontend with token. Canonical route is /api/v1/github/callback.",
    deprecated=True,
)
async def process_github_oauth_redirect(
    code: str = Query(..., description="Authorization code from GitHub"),
    state: str = Query(..., description="OAuth state parameter"),
    db: Session = Depends(get_db),
):
    """Handle browser redirect from GitHub OAuth flow and redirect to frontend with token."""
    user, token, origin = await GitHubService.authenticate_github_user(
        db=db,
        code=code,
        state=state,
    )
    target_base = origin if origin else (settings.GITHUB_REDIRECT_URI or "http://localhost:5173/auth/callback")
    if not target_base.endswith("/auth/callback"):
        target_base = f"{target_base.rstrip('/')}/auth/callback"
    separator = "&" if "?" in target_base else "?"
    redirect_target = f"{target_base}{separator}token={token}"
    return RedirectResponse(url=redirect_target)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current Authenticated User",
    description="Retrieves the profile of the currently signed-in user via Bearer token.",
)
def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Return authenticated user profile."""
    return UserResponse.model_validate(current_user)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Invalidates client-side session acknowledgement.",
)
def logout(
    current_user: User = Depends(get_current_user),
) -> LogoutResponse:
    """Acknowledge user logout."""
    return LogoutResponse(message=f"User {current_user.username} successfully logged out.")

