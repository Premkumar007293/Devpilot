"""Authentication request and response schemas."""

from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.user import UserResponse


class TokenResponse(BaseModel):
    """JWT bearer token and authenticated user payload."""
    access_token: str = Field(..., description="HS256 signed JWT access token")
    token_type: str = Field("bearer", description="Token scheme identifier")
    user: UserResponse = Field(..., description="Authenticated user profile")


class OAuthUrlResponse(BaseModel):
    """GitHub OAuth login initialization payload."""
    authorization_url: str = Field(..., description="GitHub OAuth authorization redirect URL")
    state: str = Field(..., description="Tamper-proof CSRF protection state token")


class OAuthCallbackRequest(BaseModel):
    """GitHub OAuth callback payload from frontend."""
    code: str = Field(..., description="GitHub authorization code from redirect")
    state: str = Field(..., description="CSRF state token sent during initiation")


class LogoutResponse(BaseModel):
    """Logout confirmation message."""
    message: str = "Successfully logged out."

