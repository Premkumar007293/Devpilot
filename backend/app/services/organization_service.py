"""Organization service handling organization lifecycle and membership logic."""

import uuid
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.exceptions import DevPilotException, ResourceNotFoundException
from app.core.logging import logger
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.repository import Repository
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationMemberCreate,
    OrganizationUpdate,
    generate_slug,
)


class OrganizationService:
    """Service encapsulating organization domain operations."""

    @staticmethod
    def create_organization(db: Session, org_in: OrganizationCreate) -> Organization:
        """Create a new organization record, ensuring unique slug."""
        slug = org_in.slug or generate_slug(org_in.name)

        # Check existing slug
        existing = db.scalars(select(Organization).where(Organization.slug == slug)).first()
        if existing:
            # Append short random hex to preserve uniqueness
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"

        org = Organization(
            name=org_in.name,
            slug=slug,
            description=org_in.description or "",
        )
        db.add(org)
        try:
            db.commit()
            db.refresh(org)
            logger.info("Created organization id=%s slug=%s", org.id, org.slug)
            return org
        except IntegrityError as exc:
            db.rollback()
            logger.warning("Failed to create organization due to conflict: %s", str(exc))
            raise DevPilotException(
                message=f"Organization with slug '{slug}' already exists.",
                status_code=409,
            )

    @staticmethod
    def list_organizations(
        db: Session, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Organization], int]:
        """List organizations with pagination."""
        total = db.scalar(select(func.count()).select_from(Organization)) or 0
        query = select(Organization).offset(skip).limit(limit).order_by(Organization.created_at.desc())
        items = list(db.scalars(query).all())
        return items, total

    @staticmethod
    def get_organization_by_id(db: Session, org_id: uuid.UUID) -> Optional[Organization]:
        """Fetch organization by primary UUID."""
        return db.scalar(select(Organization).where(Organization.id == org_id))

    @staticmethod
    def get_organization_by_slug(db: Session, slug: str) -> Optional[Organization]:
        """Fetch organization by unique slug."""
        return db.scalar(select(Organization).where(Organization.slug == slug))

    @staticmethod
    def update_organization(
        db: Session, org: Organization, update_in: OrganizationUpdate
    ) -> Organization:
        """Update organization details."""
        update_data = update_in.model_dump(exclude_unset=True)

        if "slug" in update_data and update_data["slug"]:
            new_slug = update_data["slug"]
            existing = db.scalars(
                select(Organization).where(
                    Organization.slug == new_slug, Organization.id != org.id
                )
            ).first()
            if existing:
                raise DevPilotException(
                    message=f"Organization with slug '{new_slug}' already exists.",
                    status_code=409,
                )

        for key, value in update_data.items():
            setattr(org, key, value)

        db.commit()
        db.refresh(org)
        logger.info("Updated organization id=%s", org.id)
        return org

    @staticmethod
    def delete_organization(db: Session, org: Organization) -> None:
        """Delete organization and cascade to dependent members and repositories."""
        org_id = org.id
        db.delete(org)
        db.commit()
        logger.info("Deleted organization id=%s", org_id)

    @staticmethod
    def add_member(
        db: Session, org: Organization, member_in: OrganizationMemberCreate
    ) -> OrganizationMember:
        """Add user to organization membership."""
        # Check existing membership
        existing = db.scalar(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == org.id,
                OrganizationMember.user_id == member_in.user_id,
            )
        )
        if existing:
            raise DevPilotException(
                message="User is already a member of this organization.",
                status_code=409,
            )

        member = OrganizationMember(
            organization_id=org.id,
            user_id=member_in.user_id,
            role=member_in.role.value if hasattr(member_in.role, "value") else str(member_in.role),
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        logger.info("Added user=%s to org=%s with role=%s", member.user_id, org.id, member.role)
        return member

    @staticmethod
    def list_members(db: Session, org_id: uuid.UUID) -> List[OrganizationMember]:
        """List all members of an organization."""
        return list(
            db.scalars(
                select(OrganizationMember)
                .where(OrganizationMember.organization_id == org_id)
                .order_by(OrganizationMember.joined_at.asc())
            ).all()
        )
