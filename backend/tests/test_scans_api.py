"""Integration tests for Scan Job lifecycle and management API endpoints."""

import uuid
from starlette.testclient import TestClient


def create_test_repository(client: TestClient) -> str:
    """Helper creating an organization and repository for scan job tests."""
    org_res = client.post(
        "/api/v1/organizations",
        json={"name": "Scan Test Org", "slug": f"scan-org-{uuid.uuid4().hex[:6]}"},
    )
    org_id = org_res.json()["id"]

    repo_res = client.post(
        "/api/v1/repositories",
        json={"organization_id": org_id, "name": f"scan-target-{uuid.uuid4().hex[:4]}"},
    )
    return repo_res.json()["id"]


def test_scan_job_lifecycle(client: TestClient):
    """Verify scan job creation, progress tracking, completion, and cancellation."""
    repo_id = create_test_repository(client)

    # 1. Create scan job without async dispatch for deterministic testing
    create_res = client.post(
        "/api/v1/scans?dispatch_async=false",
        json={"repository_id": repo_id, "scan_type": "security"},
    )
    assert create_res.status_code == 201
    scan = create_res.json()
    assert scan["status"] == "PENDING"
    assert scan["scan_type"] == "security"
    assert scan["progress"] == 0
    scan_id = scan["id"]

    # 2. Retrieve scan job details
    get_res = client.get(f"/api/v1/scans/{scan_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == scan_id

    # 3. Update scan status to RUNNING with 45% progress
    patch_res = client.patch(
        f"/api/v1/scans/{scan_id}",
        json={"status": "RUNNING", "progress": 45},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "RUNNING"
    assert patch_res.json()["progress"] == 45
    assert patch_res.json()["started_at"] is not None

    # 4. Complete scan job
    complete_res = client.patch(
        f"/api/v1/scans/{scan_id}",
        json={"status": "COMPLETED"},
    )
    assert complete_res.status_code == 200
    assert complete_res.json()["status"] == "COMPLETED"
    assert complete_res.json()["progress"] == 100
    assert complete_res.json()["completed_at"] is not None

    # Verify repository last_scanned_at was updated
    repo_res = client.get(f"/api/v1/repositories/{repo_id}")
    assert repo_res.json()["last_scanned_at"] is not None

    # 5. Cancel completed job should return 400
    cancel_res = client.post(f"/api/v1/scans/{scan_id}/cancel")
    assert cancel_res.status_code == 400


def test_scan_job_cancellation_and_filters(client: TestClient):
    """Verify scan cancellation and filtering by status and type."""
    repo_id = create_test_repository(client)

    scan_res = client.post(
        "/api/v1/scans?dispatch_async=false",
        json={"repository_id": repo_id, "scan_type": "ast"},
    )
    scan_id = scan_res.json()["id"]

    # Cancel pending job
    cancel_res = client.post(f"/api/v1/scans/{scan_id}/cancel")
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"

    # Filter scans by status
    filter_res = client.get(f"/api/v1/scans?repository_id={repo_id}&status=CANCELLED")
    assert filter_res.status_code == 200
    assert filter_res.json()["total"] == 1
    assert filter_res.json()["items"][0]["id"] == scan_id
