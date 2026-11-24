"""Tests for API root, health, and Swagger documentation endpoints."""

from starlette.testclient import TestClient


def test_api_v1_health(client: TestClient):
    """Verify GET /api/v1/health returns expected contract."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "status": "healthy",
        "application": "DevPilot",
        "version": "1.0.0",
    }


def test_api_v1_root(client: TestClient):
    """Verify GET /api/v1/ returns expected welcome message."""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "message": "Welcome to DevPilot API",
        "version": "1.0.0",
    }


def test_openapi_docs(client: TestClient):
    """Verify OpenAPI JSON schema is generated and accessible."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "DevPilot API"
    assert schema["info"]["version"] == "1.0.0"
    assert "/api/v1/health" in schema["paths"]
    assert "/api/v1/" in schema["paths"]


def test_cors_headers(client: TestClient):
    """Verify CORS middleware headers are properly returned on preflight requests."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_github_client_uses_bearer_auth_header():
    """GitHub requests must send a real bearer token instead of a placeholder."""
    from app.integrations.github.client import GitHubClient

    client = GitHubClient(token="ghp_example_token")
    headers = client._get_headers()

    assert headers["Authorization"] == "Bearer ghp_example_token"


def test_auth_and_github_routes_are_exposed(client: TestClient):
    """Authentication and GitHub integration endpoints must be mounted under /api/v1."""
    github_url = client.get("/api/v1/auth/github")
    assert github_url.status_code in (200, 503)

    protected = client.get("/api/v1/github/repositories")
    assert protected.status_code == 401


def test_github_webhook_signature_validation(client: TestClient, monkeypatch):
    """GitHub webhooks must verify HMAC signatures and prevent duplicate delivery processing."""
    import hashlib
    import hmac
    import json

    payload = json.dumps({"ref": "refs/heads/main"}).encode("utf-8")
    secret = "webhook-secret"
    from app.core import config as config_module

    monkeypatch.setattr(config_module.settings, "GITHUB_WEBHOOK_SECRET", secret)
    signature = "sha256=" + hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    response = client.post(
        "/api/v1/github/webhook",
        content=payload,
        headers={
            "X-Hub-Signature-256": signature,
            "X-GitHub-Event": "push",
            "X-GitHub-Delivery": "delivery-123",
        },
    )
    assert response.status_code == 202
    assert response.json()["status"] == "accepted"

    duplicate = client.post(
        "/api/v1/github/webhook",
        content=payload,
        headers={
            "X-Hub-Signature-256": signature,
            "X-GitHub-Event": "push",
            "X-GitHub-Delivery": "delivery-123",
        },
    )
    assert duplicate.status_code == 202
    assert duplicate.json()["status"] == "duplicate"

