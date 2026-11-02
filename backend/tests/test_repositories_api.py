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
