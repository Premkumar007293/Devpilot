"""Unit tests for SQLAlchemy models, constraints, and relationships."""

import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.organization_member import MemberRole, OrganizationMember
from app.models.repository import Repository
from app.models.scan_job import ScanJob, ScanJobStatus, ScanType
from app.models.user import User


def test_user_creation(db_session: Session):
    """Verify user model creation and unique email constraint."""
    user = User(
        email="test_user@devpilot.ai",
        username="test_user",
        full_name="Test User",
    )
    db_session.add(user)
    db_session.flush()

    assert user.id is not None
    assert isinstance(user.id, uuid.UUID)
    assert user.is_active is True
    assert user.created_at is not None

    # Duplicate email should fail
    duplicate = User(
        email="test_user@devpilot.ai",
        username="other_username",
    )
    db_session.add(duplicate)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_organization_and_relationships(db_session: Session):
    """Verify organization creation, unique slug, and cascading relationships."""
    org = Organization(
        name="DevPilot Core Team",
        slug="devpilot-core-team",
        description="Main engineering org",
    )
    db_session.add(org)
    db_session.flush()

    assert org.id is not None
    assert org.slug == "devpilot-core-team"

    # Create user and membership
    user = User(
        email="member@devpilot.ai",
        username="org_member",
    )
    db_session.add(user)
    db_session.flush()

    member = OrganizationMember(
        organization_id=org.id,
        user_id=user.id,
        role=MemberRole.OWNER.value,
    )
    db_session.add(member)
    db_session.flush()

    assert member.id is not None
    assert member.role == "OWNER"

    # Add Repository
    repo = Repository(
        organization_id=org.id,
        name="agent-engine",
        full_name="devpilot-core-team/agent-engine",
        provider="github",
        default_branch="main",
    )
    db_session.add(repo)
    db_session.flush()

    assert repo.id is not None
    assert repo.organization.id == org.id

    # Add ScanJob
    scan = ScanJob(
        repository_id=repo.id,
        status=ScanJobStatus.PENDING.value,
        scan_type=ScanType.FULL.value,
        progress=0,
    )
    db_session.add(scan)
    db_session.flush()

    assert scan.id is not None
    assert scan.repository.id == repo.id

    # Verify cascading delete
    db_session.delete(org)
    db_session.flush()

    assert db_session.get(Organization, org.id) is None
    assert db_session.get(OrganizationMember, member.id) is None
    assert db_session.get(Repository, repo.id) is None
    assert db_session.get(ScanJob, scan.id) is None


def test_unique_member_constraint(db_session: Session):
    """Verify user cannot be added twice to the same organization."""
    user = User(email="unique@devpilot.ai", username="unique_dev")
    org = Organization(name="Unique Org", slug="unique-org")
    db_session.add_all([user, org])
    db_session.flush()

    m1 = OrganizationMember(organization_id=org.id, user_id=user.id, role="MEMBER")
    db_session.add(m1)
    db_session.flush()

    m2 = OrganizationMember(organization_id=org.id, user_id=user.id, role="ADMIN")
    db_session.add(m2)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()
