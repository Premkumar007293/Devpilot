"""Security utilities and token handling foundation."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from app.core.config import settings


def create_access_token_placeholder(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a token placeholder structure for Phase 2 authentication integration."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    # Placeholder token string for Phase 1 architecture setup
    return f"devpilot_token_{subject}_{int(expire.timestamp())}"
