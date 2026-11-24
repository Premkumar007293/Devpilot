"""Unit and integration tests for GitHub OAuth callback routes and state validation."""

import pytest
from starlette.testclient import TestClient
from app.core.security import create_oauth_state


def test_github_connect_returns_canonical_redirect_uri(client: TestClient):
    """The authorization endpoint must construct a GitHub URL with the canonical redirect_uri."""
    response = client.get("/api/v1/github/connect")
    assert response.status_code == 200
    data = response.json()
    assert "authorization_url" in data
    assert "redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fapi%2Fv1%2Fgithub%2Fcallback" in data["authorization_url"]
    assert "state=" in data["authorization_url"]


def test_canonical_callback_missing_params(client: TestClient):
    """GET /api/v1/github/callback must reject requests missing code or state with 422."""
    response = client.get("/api/v1/github/callback")
    assert response.status_code == 422


def test_canonical_callback_invalid_csrf_state(client: TestClient):
    """GET /api/v1/github/callback must reject forged or expired state with 400."""
    response = client.get("/api/v1/github/callback?code=mock_code&state=forged_csrf_state")
    assert response.status_code == 400
    assert "Invalid or expired OAuth state token" in response.json()["detail"]


def test_legacy_auth_callback_invalid_csrf_state(client: TestClient):
    """GET /api/v1/auth/github/callback must also validate CSRF state and reject forged states."""
    response = client.get("/api/v1/auth/github/callback?code=mock_code&state=forged_csrf_state")
    assert response.status_code == 400
    assert "Invalid or expired OAuth state token" in response.json()["detail"]


def test_unversioned_route_removed(client: TestClient):
    """The accidental unversioned mount /api/github/callback must return 404."""
    response = client.get("/api/github/callback")
    assert response.status_code == 404

