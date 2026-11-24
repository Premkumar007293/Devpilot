"""Test beta feedback API flows."""

import uuid

from app.core.security import create_access_token
from app.models.user import User


def test_create_and_list_feedback(client, db_session):
    """Users can create feedback and retrieve their own submissions."""
    user = User(
        email=f"beta-{uuid.uuid4().hex[:8]}@devpilot.ai",
        username=f"beta_{uuid.uuid4().hex[:8]}",
        full_name="Beta User",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token({"sub": str(user.id), "username": user.username})

    response = client.post(
        "/api/v1/feedback",
        json={
            "category": "bug",
            "description": "Search modal ignores backend repository results when query is short.",
            "related_resource_type": "search",
            "related_resource_id": "search-modal",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["category"] == "bug"
    assert payload["description"].startswith("Search modal")

    list_response = client.get(
        "/api/v1/feedback",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    items = list_response.json()
    assert len(items) >= 1
    assert any(item["id"] == payload["id"] for item in items)
