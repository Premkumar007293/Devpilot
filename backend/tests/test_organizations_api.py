"""Integration tests for Organization API endpoints."""

import uuid
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User


def test_create_and_get_organization(client: TestClient):
    """Verify creating and retrieving an organization."""
    response = client.post(
        "/api/v1/organizations",
        json={"name": "Antigravity Research", "description": "AI systems lab"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Antigravity Research"
    assert data["slug"] == "antigravity-research"
    org_id = data["id"]

    # Retrieve by ID
    get_res = client.get(f"/api/v1/organizations/{org_id}")
    assert get_res.status_code == 200
    assert get_res.json()["slug"] == "antigravity-research"


def test_list_organizations_pagination(client: TestClient):
    """Verify listing organizations with pagination."""
    # Create multiple organizations
    for i in range(3):
        client.post(
            "/api/v1/organizations",
            json={"name": f"Org Batch {i}", "slug": f"org-batch-{i}-{uuid.uuid4().hex[:4]}"},
        )

    response = client.get("/api/v1/organizations?skip=0&limit=2")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert len(body["items"]) <= 2
    assert body["limit"] == 2


def test_update_and_delete_organization(client: TestClient):
    """Verify updating and deleting an organization."""
    res = client.post(
        "/api/v1/organizations",
        json={"name": "Updatable Org", "slug": f"updatable-{uuid.uuid4().hex[:4]}"},
    )
    org_id = res.json()["id"]

    # Update name
    patch_res = client.patch(
        f"/api/v1/organizations/{org_id}",
        json={"name": "Renamed Org", "description": "Updated description"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["name"] == "Renamed Org"

    # Delete
    del_res = client.delete(f"/api/v1/organizations/{org_id}")
    assert del_res.status_code == 204

    # Verify not found after deletion
    get_res = client.get(f"/api/v1/organizations/{org_id}")
    assert get_res.status_code == 404


def test_organization_members_api(client: TestClient, db_session: Session):
    """Verify adding and listing organization members."""
    # Seed a user directly
    user = User(
        email=f"member_{uuid.uuid4().hex[:6]}@devpilot.ai",
        username=f"user_{uuid.uuid4().hex[:6]}",
        full_name="Member Dev",
    )
    db_session.add(user)
    db_session.commit()

    org_res = client.post(
        "/api/v1/organizations",
        json={"name": "Member Test Org", "slug": f"member-org-{uuid.uuid4().hex[:4]}"},
    )
    org_id = org_res.json()["id"]

    # Add member
    add_res = client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": str(user.id), "role": "ADMIN"},
    )
    assert add_res.status_code == 201
    assert add_res.json()["role"] == "ADMIN"

    # List members
    list_res = client.get(f"/api/v1/organizations/{org_id}/members")
    assert list_res.status_code == 200
    members = list_res.json()
    assert len(members) == 1
    assert members[0]["user_id"] == str(user.id)

    # Adding duplicate member returns 409
    dup_res = client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": str(user.id), "role": "MEMBER"},
    )
    assert dup_res.status_code == 409
