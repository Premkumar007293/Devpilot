"""Integration tests for Repository management API endpoints."""

import uuid
from starlette.testclient import TestClient


def create_test_organization(client: TestClient) -> str:
    """Helper creating a parent organization for repository tests."""
    res = client.post(
        "/api/v1/organizations",
        json={"name": "Repo Test Org", "slug": f"repo-org-{uuid.uuid4().hex[:6]}"},
    )
    assert res.status_code == 201
    return res.json()["id"]


def test_repository_crud_and_validation(client: TestClient):
    """Verify repository creation, reading, updating, and deletion."""
    org_id = create_test_organization(client)

    # 1. Create repository
    repo_payload = {
        "organization_id": org_id,
        "name": "neural-parser",
        "description": "Code graph parser",
        "provider": "github",
        "default_branch": "main",
        "is_private": True,
        "is_active": True,
    }
    create_res = client.post("/api/v1/repositories", json=repo_payload)
    assert create_res.status_code == 201
    repo = create_res.json()
    assert repo["name"] == "neural-parser"
    assert repo["is_private"] is True
    repo_id = repo["id"]

    # Duplicate repo in same org returns 409
    dup_res = client.post("/api/v1/repositories", json=repo_payload)
    assert dup_res.status_code == 409

    # 2. Get repository by ID
    get_res = client.get(f"/api/v1/repositories/{repo_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "neural-parser"

    # 3. Update repository metadata
    patch_res = client.patch(
        f"/api/v1/repositories/{repo_id}",
        json={"description": "Updated neural parser description", "is_private": False},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["description"] == "Updated neural parser description"
    assert patch_res.json()["is_private"] is False

    # 4. Delete repository
    del_res = client.delete(f"/api/v1/repositories/{repo_id}")
    assert del_res.status_code == 204

    # Verify not found after deletion
    assert client.get(f"/api/v1/repositories/{repo_id}").status_code == 404


def test_repository_filtering_and_pagination(client: TestClient):
    """Verify listing repositories with filters and pagination."""
    org_id = create_test_organization(client)

    # Create 3 repositories with different flags
    client.post(
        "/api/v1/repositories",
        json={
            "organization_id": org_id,
            "name": f"public-active-{uuid.uuid4().hex[:4]}",
            "provider": "github",
            "is_private": False,
            "is_active": True,
        },
    )
    client.post(
        "/api/v1/repositories",
        json={
            "organization_id": org_id,
            "name": f"private-active-{uuid.uuid4().hex[:4]}",
            "provider": "github",
            "is_private": True,
            "is_active": True,
        },
    )
    client.post(
        "/api/v1/repositories",
        json={
            "organization_id": org_id,
            "name": f"public-inactive-{uuid.uuid4().hex[:4]}",
            "provider": "gitlab",
            "is_private": False,
            "is_active": False,
        },
    )

    # Filter by organization and private
    res = client.get(f"/api/v1/repositories?organization_id={org_id}&is_private=true")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["is_private"] is True

    # Filter by provider
    gitlab_res = client.get(f"/api/v1/repositories?organization_id={org_id}&provider=gitlab")
    assert gitlab_res.status_code == 200
    assert gitlab_res.json()["total"] == 1
    assert gitlab_res.json()["items"][0]["provider"] == "gitlab"

    # Pagination
    page_res = client.get(f"/api/v1/repositories?organization_id={org_id}&skip=0&limit=2")
    assert page_res.status_code == 200
    assert len(page_res.json()["items"]) == 2


def test_repository_connect_and_ingestion_routes(client: TestClient, db_session, monkeypatch):
    """Verify GitHub repository connection and ingestion routes work with mocked GitHub responses."""
    from app.core.auth import get_current_user
    from app.integrations.github.client import GitHubClient
    from app.main import app as fastapi_app
    from app.models.user import User

    user = User(
        email="connected_user@devpilot.ai",
        username="connected_user",
        full_name="Connected User",
        github_access_token="ghp_test_token",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    org_res = client.post(
        "/api/v1/organizations",
        json={"name": "Connected Org", "slug": f"connected-org-{uuid.uuid4().hex[:4]}"},
    )
    org_id = org_res.json()["id"]

    async def fake_list_user_repositories(self, per_page=100):
        return [{
            "id": 42,
            "name": "demo-repo",
            "full_name": "acme/demo-repo",
            "description": "Demo repository",
            "html_url": "https://github.com/acme/demo-repo",
            "default_branch": "main",
            "private": False,
            "language": "Python",
            "stargazers_count": 9,
        }]

    async def fake_get_repository_tree(self, owner: str, repo: str, branch: str = "main"):
        return {
            "sha": "tree-sha",
            "tree": [
                {"path": "app/main.py", "type": "blob", "size": 128, "sha": "blob1"},
                {"path": "node_modules/dep/index.js", "type": "blob", "size": 32, "sha": "blob2"},
            ],
        }

    monkeypatch.setattr(GitHubClient, "list_user_repositories", fake_list_user_repositories)
    monkeypatch.setattr(GitHubClient, "get_repository_tree", fake_get_repository_tree)

    fastapi_app.dependency_overrides[get_current_user] = lambda: user
    try:
        connect_res = client.post(
            "/api/v1/repositories/connect",
            json={"github_repo_id": 42, "organization_id": org_id},
        )
        assert connect_res.status_code == 201
        repo_id = connect_res.json()["id"]

        file_res = client.get(f"/api/v1/repositories/{repo_id}/files")
        assert file_res.status_code == 200

        ingest_res = client.post(f"/api/v1/repositories/{repo_id}/ingest?branch=main")
        assert ingest_res.status_code == 201
        assert ingest_res.json()["status"] == "COMPLETED"

        status_res = client.get(f"/api/v1/repositories/{repo_id}/ingestion")
        assert status_res.status_code == 200
        assert status_res.json()["status"] == "COMPLETED"
    finally:
        fastapi_app.dependency_overrides.pop(get_current_user, None)


def test_repository_ai_engineering_endpoints(client: TestClient, db_session):
    """Advanced AI engineering endpoints should return structured repository intelligence without modifying code."""
    from app.core.security import create_access_token
    from app.models.organization_member import OrganizationMember, MemberRole
    from app.models.repository_file import RepositoryFile
    from app.models.user import User

    user = User(
        email=f"ai_engineer_{uuid.uuid4().hex[:8]}@devpilot.ai",
        username=f"ai_engineer_{uuid.uuid4().hex[:8]}",
        full_name="AI Engineer",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    org_res = client.post(
        "/api/v1/organizations",
        json={"name": "Engineering Org", "slug": f"engineering-org-{uuid.uuid4().hex[:6]}"},
    )
    org_id = org_res.json()["id"]
    db_session.add(OrganizationMember(organization_id=uuid.UUID(org_id), user_id=user.id, role=MemberRole.ADMIN.value))
    db_session.commit()

    repo_res = client.post(
        "/api/v1/repositories",
        json={
            "organization_id": org_id,
            "name": "debug-helper",
            "full_name": "engineering-org/debug-helper",
            "provider": "github",
            "default_branch": "main",
            "is_private": False,
            "is_active": True,
        },
    )
    repo_id = repo_res.json()["id"]

    db_session.add_all([
        RepositoryFile(
            repository_id=uuid.UUID(repo_id),
            path="backend/app/services/auth_service.py",
            name="auth_service.py",
            extension=".py",
            file_type="source",
            content="def validate_token(token):\n    if not token:\n        return False\n    return token.startswith('Bearer ')\n",
        ),
        RepositoryFile(
            repository_id=uuid.UUID(repo_id),
            path="backend/app/api/endpoints/auth.py",
            name="auth.py",
            extension=".py",
            file_type="source",
            content="def login_user(request):\n    token = request.headers.get('Authorization')\n    return validate_token(token)\n",
        ),
    ])
    db_session.commit()

    token = create_access_token({"sub": str(user.id), "username": user.username})
    headers = {"Authorization": f"Bearer {token}"}

    understand_res = client.get(f"/api/v1/repositories/{repo_id}/intelligence", headers=headers)
    assert understand_res.status_code == 200
    assert "file_level_understanding" in understand_res.json()

    debug_res = client.post(f"/api/v1/repositories/{repo_id}/debug?problem=Why is auth failing when the token is missing?", headers=headers)
    assert debug_res.status_code == 200
    assert "possible_root_cause" in debug_res.json()

    refactor_res = client.get(f"/api/v1/repositories/{repo_id}/refactors", headers=headers)
    assert refactor_res.status_code == 200
    assert isinstance(refactor_res.json(), list)

    tests_res = client.post(f"/api/v1/repositories/{repo_id}/tests/generate?target_symbol=validate_token", headers=headers)
    assert tests_res.status_code == 200
    assert "tests" in tests_res.json()
