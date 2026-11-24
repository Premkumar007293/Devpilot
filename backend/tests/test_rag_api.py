"""Repository RAG regression tests."""

import uuid

from app.core.auth import get_current_user
from app.main import app as fastapi_app
from app.models.organization import Organization
from app.models.repository import Repository
from app.models.repository_file import RepositoryFile
from app.models.user import User


def test_repository_rag_question_answering(client, db_session):
    """Repository ask endpoint should ground answers in retrieved file context."""
    user = User(
        email="rag-user@devpilot.ai",
        username="rag-user",
        full_name="RAG User",
        github_access_token="ghp_test",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    org = Organization(
        name="RAG Workspace",
        slug=f"rag-workspace-{uuid.uuid4().hex[:6]}",
        description="Workspace used for repository RAG tests.",
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)

    repo = Repository(
        organization_id=org.id,
        owner_user_id=user.id,
        name="auth-service",
        full_name="rag-user/auth-service",
        description="Authentication helper",
        provider="github",
        default_branch="main",
        is_private=False,
        is_active=True,
    )
    db_session.add(repo)
    db_session.commit()
    db_session.refresh(repo)

    file = RepositoryFile(
        repository_id=repo.id,
        path="app/auth.py",
        name="auth.py",
        extension=".py",
        size_bytes=512,
        file_type="source",
        content="""
def login(username, password):
    if not username or not password:
        raise ValueError('Missing credentials')
    return {'status': 'authenticated'}
""",
        is_binary=False,
        branch="main",
    )
    db_session.add(file)
    db_session.commit()
    db_session.refresh(file)

    fastapi_app.dependency_overrides[get_current_user] = lambda: user
    try:
        response = client.post(
            f"/api/v1/repositories/{repo.id}/ask?question=How%20does%20authentication%20work%20in%20this%20project?",
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["retrieval_count"] >= 1
        assert payload["citations"]
        assert "answer" in payload
    finally:
        fastapi_app.dependency_overrides.pop(get_current_user, None)
