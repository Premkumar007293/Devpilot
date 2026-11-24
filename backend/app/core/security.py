from __future__ import annotations
"""Security utilities: RFC 7519 JWT implementation and cryptographic CSRF state validation."""

import base64
import hashlib
import hmac
import json
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple
from app.core.config import settings
from app.core.logging import logger

OAUTH_STATE_STORE: Dict[str, Dict[str, Any]] = {}


def _b64_encode(data: bytes) -> str:
    """URL-safe base64 encode without padding."""
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64_decode(data_str: str) -> bytes:
    """URL-safe base64 decode with proper padding restitution."""
    padding = len(data_str) % 4
    if padding:
        data_str += "=" * (4 - padding)
    return base64.urlsafe_b64decode(data_str)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate an RFC 7519 compliant HS256 signed JSON Web Token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = data.copy()
    payload["exp"] = int(expire.timestamp())
    payload["iat"] = int(datetime.now(timezone.utc).timestamp())

    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _b64_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    signature = hmac.new(
        settings.JWT_SECRET_KEY.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    sig_b64 = _b64_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify signature and expiration of HS256 JWT, returning payload dictionary if valid."""
    try:
        parts = token.strip().split(".")
        if len(parts) != 3:
            return None

        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(
            settings.JWT_SECRET_KEY.encode("utf-8"),
            signing_input,
            hashlib.sha256,
        ).digest()

        actual_sig = _b64_decode(sig_b64)
        if not hmac.compare_digest(expected_sig, actual_sig):
            logger.warning("JWT token signature mismatch")
            return None

        payload_bytes = _b64_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Verify expiration
        exp = payload.get("exp")
        if exp and int(time.time()) > exp:
            logger.warning("JWT token has expired")
            return None

        return payload
    except Exception as exc:
        logger.warning("JWT decode error: %s", str(exc))
        return None


def create_oauth_state(user_id: Optional[str] = None, redirect_origin: Optional[str] = None) -> str:
    """Generate a tamper-proof, signed OAuth state token to prevent CSRF attacks."""
    nonce = secrets.token_hex(16)
    timestamp = str(int(time.time()))
    u_part = user_id or ""
    orig_b64 = _b64_encode(redirect_origin.encode("utf-8")) if redirect_origin else ""
    payload = f"{nonce}:{timestamp}:{u_part}:{orig_b64}"
    sig = hmac.new(
        settings.JWT_SECRET_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    state = f"{payload}:{sig}"
    OAUTH_STATE_STORE[state] = {"user_id": user_id, "origin": redirect_origin, "created_at": time.time()}
    return state


def verify_oauth_state(state: str, user_id: Optional[str] = None, max_age_seconds: int = 600) -> bool:
    """Validate OAuth state token integrity, origin signature, and expiration."""
    try:
        parts = state.strip().split(":")
        if len(parts) == 5:
            nonce, timestamp_str, u_part, orig_b64, sig = parts
            payload = f"{nonce}:{timestamp_str}:{u_part}:{orig_b64}"
        elif len(parts) == 3:
            nonce, timestamp_str, sig = parts
            payload = f"{nonce}:{timestamp_str}"
            u_part = ""
        else:
            return False

        expected_sig = hmac.new(
            settings.JWT_SECRET_KEY.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected_sig, sig):
            logger.warning("OAuth state signature verification failed")
            return False

        ts = int(timestamp_str)
        if int(time.time()) - ts > max_age_seconds or int(time.time()) < ts - 60:
            logger.warning("OAuth state has expired")
            return False

        if user_id is not None and u_part and u_part != user_id:
            logger.warning("OAuth state is not bound to the requesting user")
            return False

        return True
    except Exception as exc:
        logger.warning("OAuth state validation error: %s", str(exc))
        return False


def consume_oauth_state(state: str, max_age_seconds: int = 600) -> Tuple[Optional[str], Optional[str]]:
    """Validate a one-time OAuth state and return (user_id, redirect_origin)."""
    if not state or not verify_oauth_state(state, max_age_seconds=max_age_seconds):
        return None, None

    entry = OAUTH_STATE_STORE.pop(state, None)
    user_id = entry.get("user_id") if entry else None
    origin = entry.get("origin") if entry else None

    # Fallback to decode directly from state string payload if store was cleared
    parts = state.strip().split(":")
    if len(parts) == 5:
        _, _, u_part, orig_b64, _ = parts
        if not user_id and u_part:
            user_id = u_part
        if not origin and orig_b64:
            try:
                origin = _b64_decode(orig_b64).decode("utf-8")
            except Exception:
                pass

    return user_id, origin
