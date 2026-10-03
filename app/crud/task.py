from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import (
    Task,
    TaskPriority,
    TaskStatus,
)

async def get_task(db: AsyncSession, task_id: UUID,):
    
    result = await db.execute(
        select(Task).where(
            Task.id == task_id
        )
    )

    return result.scalar_one_or_none()

async def create_task( db: AsyncSession, project_id: UUID, user_id: UUID, title: str, description: str | None, assigned_to: UUID | None, priority: TaskPriority, due_date,):
    
    task = Task(
        project_id=project_id,
        created_by=user_id,
        assigned_to=assigned_to,
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
        status=TaskStatus.TODO,
    )

    db.add(task)

    await db.commit()

    await db.refresh(task)

    return task

async def update_task(db: AsyncSession, task: Task, title: str | None = None, description: str | None = None, due_date=None,):
    
    if title is not None:
        task.title = title

    if description is not None:
        task.description = description

    if due_date is not None:
        task.due_date = due_date

    await db.commit()

    await db.refresh(task)

    return task

async def delete_task(db: AsyncSession, task: Task,):
    
    await db.delete(task)

    await db.commit()
    
async def assign_task(db: AsyncSession, task: Task, user_id: UUID | None,):
    
    task.assigned_to = user_id

    await db.commit()

    await db.refresh(task)

    return task

async def update_task_status( db: AsyncSession, task: Task, status: TaskStatus, ):
    task.status = status

    await db.commit()

    await db.refresh(task)

    return task

async def update_task_priority(db: AsyncSession, task: Task, priority: TaskPriority,):
    
    task.priority = priority

    await db.commit()

    await db.refresh(task)

    return task

async def get_project_tasks(
    db: AsyncSession,
    project_id: UUID,
    page: int = 1,
    page_size: int = 10,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assigned_to: UUID | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    base_query = select(Task).where(
        Task.project_id == project_id
    )

    count_query = select(
        func.count(Task.id)
    ).where(
        Task.project_id == project_id
    )

    # Status filter
    if status is not None:
        base_query = base_query.where(
            Task.status == status
        )

        count_query = count_query.where(
            Task.status == status
        )

    # Priority filter
    if priority is not None:
        base_query = base_query.where(
            Task.priority == priority
        )

        count_query = count_query.where(
            Task.priority == priority
        )

    # Assignee filter
    if assigned_to is not None:
        base_query = base_query.where(
            Task.assigned_to == assigned_to
        )

        count_query = count_query.where(
            Task.assigned_to == assigned_to
        )

    # Search
    if search:
        search_pattern = f"%{search}%"

        search_filter = (
            Task.title.ilike(search_pattern)
            | Task.description.ilike(search_pattern)
        )

        base_query = base_query.where(
            search_filter
        )

        count_query = count_query.where(
            search_filter
        )

    # Sorting
    sort_columns = {
        "created_at": Task.created_at,
        "updated_at": Task.updated_at,
        "due_date": Task.due_date,
        "title": Task.title,
        "priority": Task.priority,
    }

    sort_column = sort_columns.get(
        sort_by,
        Task.created_at,
    )

    if sort_order == "asc":
        base_query = base_query.order_by(
            sort_column.asc()
        )
    else:
        base_query = base_query.order_by(
            sort_column.desc()
        )

    # Count
    total_result = await db.execute(
        count_query
    )

    total = total_result.scalar_one()

    # Pagination
    offset = (page - 1) * page_size

    base_query = base_query.offset(
        offset
    ).limit(
        page_size
    )

    result = await db.execute(
        base_query
    )

    tasks = result.scalars().all()

    return tasks, total