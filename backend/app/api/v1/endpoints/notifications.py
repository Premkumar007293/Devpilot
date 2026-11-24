"""Notification endpoints for user-facing DevPilot events."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database.session import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationCountResponse, NotificationCreate, NotificationResponse

router = APIRouter()


@router.get(
    "",
    response_model=list[NotificationResponse],
    summary="List notifications",
    description="Return recent notifications for the current user, optionally restricted to unread items.",
)
def list_notifications(
    unread_only: bool = Query(default=False, description="Only return unread notifications"),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Notification]:
    stmt = select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc())
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    stmt = stmt.limit(limit)
    notifications = db.scalars(stmt).all()
    return notifications


@router.get(
    "/unread-count",
    response_model=NotificationCountResponse,
    summary="Get unread notification count",
)
def unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationCountResponse:
    count = db.scalar(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.is_read.is_(False),
        )
    )
    return NotificationCountResponse(count=count or 0)


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a notification",
)
def create_notification(
    payload: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Notification:
    notification = Notification(
        user_id=current_user.id,
        organization_id=payload.organization_id,
        repository_id=payload.repository_id,
        title=payload.title,
        message=payload.message,
        notification_type=payload.notification_type,
        severity=payload.severity,
        related_resource_type=payload.related_resource_type,
        related_resource_id=payload.related_resource_id,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark a notification as read",
)
def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Notification:
    notification = db.get(Notification, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


@router.patch(
    "/read-all",
    response_model=list[NotificationResponse],
    summary="Mark all notifications as read",
)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Notification]:
    notifications = db.scalars(
        select(Notification).where(Notification.user_id == current_user.id, Notification.is_read.is_(False))
    ).all()
    for notification in notifications:
        notification.is_read = True
    db.commit()
    return notifications


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a notification",
)
def delete_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    notification = db.get(Notification, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    db.delete(notification)
    db.commit()
