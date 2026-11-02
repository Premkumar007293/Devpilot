"""Organization API endpoints."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.exceptions import ResourceNotFoundException
from app.database.session import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationMemberCreate,
    OrganizationMemberResponse,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.services.organization_service import OrganizationService

router = APIRouter()


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Organization",
    description="Registers a new organization with a unique slug.",
)
def create_organization(
    org_in: OrganizationCreate,
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    """Create a new organization."""
    org = OrganizationService.create_organization(db=db, org_in=org_in)
    return OrganizationResponse.model_validate(org)


@router.get(
    "",
    response_model=PaginatedResponse[OrganizationResponse],
    status_code=status.HTTP_200_OK,
    summary="List Organizations",
    description="Retrieves a paginated collection of organizations.",
)
def list_organizations(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Records per page"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[OrganizationResponse]:
    """List organizations with pagination."""
    items, total = OrganizationService.list_organizations(db=db, skip=skip, limit=limit)
    return PaginatedResponse[OrganizationResponse](
        items=[OrganizationResponse.model_validate(item) for item in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{org_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Organization Details",
    description="Fetches an organization by its UUID identifier.",
)
def get_organization(
    org_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    """Get single organization by UUID."""
    org = OrganizationService.get_organization_by_id(db=db, org_id=org_id)
    if not org:
        raise ResourceNotFoundException("Organization", org_id)
    return OrganizationResponse.model_validate(org)


@router.patch(
    "/{org_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Organization",
    description="Updates organization metadata or slug.",
)
def update_organization(
    org_id: uuid.UUID,
    org_update: OrganizationUpdate,
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    """Update organization attributes."""
    org = OrganizationService.get_organization_by_id(db=db, org_id=org_id)
    if not org:
        raise ResourceNotFoundException("Organization", org_id)
    updated = OrganizationService.update_organization(db=db, org=org, update_in=org_update)
    return OrganizationResponse.model_validate(updated)


@router.delete(
    "/{org_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Organization",
    description="Permanently deletes an organization and cascades to repositories.",
)
def delete_organization(
    org_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    """Delete organization by UUID."""
    org = OrganizationService.get_organization_by_id(db=db, org_id=org_id)
    if not org:
        raise ResourceNotFoundException("Organization", org_id)
    OrganizationService.delete_organization(db=db, org=org)


@router.get(
    "/{org_id}/members",
    response_model=List[OrganizationMemberResponse],
    status_code=status.HTTP_200_OK,
    summary="List Organization Members",
    description="Retrieves all members associated with an organization.",
)
def list_organization_members(
    org_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> List[OrganizationMemberResponse]:
    """List members of an organization."""
    org = OrganizationService.get_organization_by_id(db=db, org_id=org_id)
    if not org:
        raise ResourceNotFoundException("Organization", org_id)
    members = OrganizationService.list_members(db=db, org_id=org_id)
    return [OrganizationMemberResponse.model_validate(m) for m in members]


@router.post(
    "/{org_id}/members",
    response_model=OrganizationMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Organization Member",
    description="Associates a user with an organization under a specific role.",
)
def add_organization_member(
    org_id: uuid.UUID,
    member_in: OrganizationMemberCreate,
    db: Session = Depends(get_db),
) -> OrganizationMemberResponse:
    """Add a member to an organization."""
    org = OrganizationService.get_organization_by_id(db=db, org_id=org_id)
    if not org:
        raise ResourceNotFoundException("Organization", org_id)
    member = OrganizationService.add_member(db=db, org=org, member_in=member_in)
    return OrganizationMemberResponse.model_validate(member)
