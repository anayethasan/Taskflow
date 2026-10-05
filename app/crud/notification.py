from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationType


async def create_notification(
    db: AsyncSession,
    user_id: UUID,
    notification_type: NotificationType,
    title: str,
    message: str,
    task_id: UUID | None = None,
):
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        task_id=task_id,
    )

    db.add(notification)

    await db.commit()
    await db.refresh(notification)

    return notification


async def get_user_notifications(
    db: AsyncSession,
    user_id: UUID,
    page: int = 1,
    page_size: int = 20,
    unread_only: bool = False,
):
    base_query = select(Notification).where(
        Notification.user_id == user_id
    )

    count_query = select(func.count(Notification.id)).where(
        Notification.user_id == user_id
    )

    if unread_only:
        base_query = base_query.where(
            Notification.is_read.is_(False)
        )

        count_query = count_query.where(
            Notification.is_read.is_(False)
        )

    base_query = base_query.order_by(
        Notification.created_at.desc()
    )

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    offset = (page - 1) * page_size

    result = await db.execute(
        base_query
        .offset(offset)
        .limit(page_size)
    )

    notifications = result.scalars().all()

    return notifications, total


async def get_notification(db: AsyncSession,notification_id: UUID,):
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id
        )
    )

    return result.scalar_one_or_none()


async def mark_notification_as_read(db: AsyncSession,notification: Notification,):
    notification.is_read = True

    await db.commit()
    await db.refresh(notification)

    return notification