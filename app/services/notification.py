from uuid import UUID

from app.crud.notification import create_notification
from app.database.session import SessionLocal
from app.models.notification import NotificationType


async def send_task_assigned_notification(
    user_id: UUID,
    task_id: UUID,
    task_title: str,
):
    async with SessionLocal() as db:
        await create_notification(
            db=db,
            user_id=user_id,
            notification_type=NotificationType.TASK_ASSIGNED,
            title="Task Assigned",
            message=f'You have been assigned the task "{task_title}".',
            task_id=task_id,
        )


async def send_task_status_notification(
    user_id: UUID,
    task_id: UUID,
    task_title: str,
    status: str,
):
    async with SessionLocal() as db:
        await create_notification(
            db=db,
            user_id=user_id,
            notification_type=NotificationType.TASK_STATUS_CHANGED,
            title="Task Status Updated",
            message=(
                f'The task "{task_title}" status changed '
                f'to "{status}".'
            ),
            task_id=task_id,
        )