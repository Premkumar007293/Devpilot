"""Beta feedback endpoints for bug reports and product feedback."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database.session import get_db
from app.models.feedback import Feedback
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackResponse

router = APIRouter()


@router.get(
    "",
    response_model=list[FeedbackResponse],
    summary="List feedback submissions",
)
def list_feedback(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Feedback]:
    items = db.scalars(
        select(Feedback)
        .where(Feedback.user_id == current_user.id)
        .order_by(Feedback.created_at.desc())
        .limit(limit)
    ).all()
    return items


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a feedback submission",
)
def create_feedback(
    payload: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Feedback:
    item = Feedback(
        user_id=current_user.id,
        category=payload.category,
        description=payload.description,
        repository_id=payload.repository_id,
        related_resource_type=payload.related_resource_type,
        related_resource_id=payload.related_resource_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get(
    "/{feedback_id}",
    response_model=FeedbackResponse,
    summary="Fetch a feedback item by id",
)
def get_feedback(
    feedback_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Feedback:
    item = db.get(Feedback, feedback_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback item not found")
    return item
