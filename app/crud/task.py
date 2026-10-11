
from datetime import date
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskPriority, TaskStatus


# =========================
# Get Task
# =========================
async def get_task(
    db: AsyncSession,
    task_id: UUID,
) -> Task | None:
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )

    return result.scalar_one_or_none()


# =========================
# Create Task
# =========================
async def create_task(
    db: AsyncSession,
    project_id: UUID,
    user_id: UUID,
    title: str,
    description: str | None = None,
    assigned_to: UUID | None = None,
    priority: TaskPriority = TaskPriority.MEDIUM,
    due_date: date | None = None,
) -> Task:
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

    try:
        db.add(task)
        await db.commit()
        await db.refresh(task)
    except Exception:
        await db.rollback()
        raise

    return task


# =========================
# Update Task
# =========================
async def update_task(
    db: AsyncSession,
    task: Task,
    title: str | None = None,
    description: str | None = None,
    due_date: date | None = None,
) -> Task:
    if title is not None:
        task.title = title

    if description is not None:
        task.description = description

    if due_date is not None:
        task.due_date = due_date

    try:
        await db.commit()
        await db.refresh(task)
    except Exception:
        await db.rollback()
        raise

    return task


# =========================
# Delete Task
# =========================
async def delete_task(
    db: AsyncSession,
    task: Task,
) -> None:
    try:
        await db.delete(task)
        await db.commit()
    except Exception:
        await db.rollback()
        raise


# =========================
# Assign / Unassign Task
# =========================
async def assign_task(
    db: AsyncSession,
    task: Task,
    user_id: UUID | None,
) -> Task:
    task.assigned_to = user_id

    try:
        await db.commit()
        await db.refresh(task)
    except Exception:
        await db.rollback()
        raise

    return task


# =========================
# Update Task Status
# =========================
async def update_task_status(
    db: AsyncSession,
    task: Task,
    status: TaskStatus,
) -> Task:
    task.status = status

    try:
        await db.commit()
        await db.refresh(task)
    except Exception:
        await db.rollback()
        raise

    return task


# =========================
# Update Task Priority
# =========================
async def update_task_priority(
    db: AsyncSession,
    task: Task,
    priority: TaskPriority,
) -> Task:
    task.priority = priority

    try:
        await db.commit()
        await db.refresh(task)
    except Exception:
        await db.rollback()
        raise

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
) -> tuple[list[Task], int]:

    # Validate pagination
    if page < 1:
        raise ValueError("Page must be greater than or equal to 1")

    if not 1 <= page_size <= 100:
        raise ValueError("Page size must be between 1 and 100")

    # Validate sorting order
    if sort_order not in {"asc", "desc"}:
        raise ValueError("Sort order must be 'asc' or 'desc'")

    # Allowed sorting columns
    sort_columns = {
        "created_at": Task.created_at,
        "updated_at": Task.updated_at,
        "due_date": Task.due_date,
        "title": Task.title,
        "priority": Task.priority,
    }

    sort_column = sort_columns.get(sort_by)

    if sort_column is None:
        raise ValueError("Invalid sort_by field")

    # Base filters
    filters = [
        Task.project_id == project_id,
    ]

    # Status filter
    if status is not None:
        filters.append(Task.status == status)

    # Priority filter
    if priority is not None:
        filters.append(Task.priority == priority)

    # Assigned user filter
    if assigned_to is not None:
        filters.append(Task.assigned_to == assigned_to)

    # Search by title or description
    if search and search.strip():
        search_pattern = f"%{search.strip()}%"

        filters.append(
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern),
            )
        )

    # Main query
    base_query = (
        select(Task)
        .where(*filters)
    )

    # Count query
    count_query = (
        select(func.count(Task.id))
        .where(*filters)
    )

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Sorting
    if sort_order == "asc":
        base_query = base_query.order_by(
            sort_column.asc().nulls_last(),
            Task.id.asc(),
        )
    else:
        base_query = base_query.order_by(
            sort_column.desc().nulls_last(),
            Task.id.asc(),
        )

    # Pagination
    offset = (page - 1) * page_size

    base_query = (
        base_query
        .offset(offset)
        .limit(page_size)
    )

    # Execute query
    result = await db.execute(base_query)
    tasks = list(result.scalars().all())

    return tasks, total
