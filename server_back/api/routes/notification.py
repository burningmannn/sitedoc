import logging
from typing import List

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from core.models.models import Notification
from core.schemas import NotificationCreate
from core.security import get_current_user

router = APIRouter(prefix='/api/notification', tags=['Notification'])
error_logger = logging.getLogger("errors")
action_logger = logging.getLogger("actions")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_notification(
        notification_data: NotificationCreate,
        db: AsyncSession = Depends(get_async_session),
        user=Depends(get_current_user)
):
    new_notification = Notification(
        file_id=notification_data.file_id,
        user_id=user.id,
        message=notification_data.message,
    )
    db.add(new_notification)
    await db.commit()
    return {"message": "Уведомление создано"}


@router.get("/", response_model=List[dict])
async def get_notifications(
        db: AsyncSession = Depends(get_async_session),
        user=Depends(get_current_user)
):
    if not user:
        return []
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user.id)
        .where(Notification.is_read == False)
        .order_by(Notification.created_at.desc())
    )
    notifications = result.scalars().all()

    return [
        {
            "id": n.id,
            "file_id": n.file_id,
            "message": n.message,
            "created_at": n.created_at.isoformat(),
            "is_read": n.is_read
        }
        for n in notifications
    ]


@router.patch("/{notification_id}/read")
async def mark_as_read(
        notification_id: int,
        db: AsyncSession = Depends(get_async_session),
        user=Depends(get_current_user)
):
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id, Notification.user_id == user.id)
    )
    notification = result.scalar_one_or_none()
    if not notification:
        error_logger.error(f'Ошибка прочтения уведомления {notification}, так как оно не найдено')
        raise HTTPException(status_code=404, detail="Уведомление не найдено")

    notification.is_read = True
    await db.commit()
    action_logger.info(f'{user} прочитал уведомление {notification}')
    return {"message": "Отмечено как прочитанное"}
