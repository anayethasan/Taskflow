from math import ceil
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_current_user,
    require_project_permission,
)
from app.crud import task as task_crud
from app.crud.project import get_project_membership
from app.database.session import get_db
from app.models.task import (
    TaskPriority,
    TaskStatus,
)
from app.models.user import User
from app.schemas.task import (
    TaskAssignmentUpdate,
    TaskCreate,
    TaskListResponse,
    TaskPriorityEnum,
    TaskPriorityUpdate,
    TaskResponse,
    TaskStatusEnum,
    TaskStatusUpdate,
    TaskUpdate,
)

router = APIRouter(
    tags=["Tasks"],
)

@router.post("/projects/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    project_id: UUID,
    data: TaskCreate,
    current_user: User = Depends(
        get_current_user
    ), db: AsyncSession = Depends(get_db),):
    
    await require_project_permission(
        project_id,
        "update_project",
        current_user,
        db,
    )

    # If task is assigned during creation,
    # verify that user belongs to project.
    if data.assigned_to is not None:

        assignee = await get_project_membership(
            db,
            project_id,
            data.assigned_to,
        )

        if not assignee:
            raise HTTPException(
                status_code=400,
                detail="Assigned user is not a project member",
            )

    task = await task_crud.create_task(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
        title=data.title,
        description=data.description,
        assigned_to=data.assigned_to,
        priority=TaskPriority(data.priority.value),
        due_date=data.due_date,
    )

    return task

@router.get("/tasks/{task_id}",
    response_model=TaskResponse,
)
async def get_task(
    task_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    
    task = await task_crud.get_task(
        db,
        task_id,
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    await require_project_permission(
        task.project_id,
        "view_project",
        current_user,
        db,
    )

    return task


@router.get("/projects/{project_id}/tasks",
    response_model=TaskListResponse,
)
async def list_tasks(
    project_id: UUID,

    page: int = Query(
        default=1,
        ge=1,
    ),

    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
    ),

    status_filter: TaskStatusEnum | None = Query(
        default=None,
        alias="status",
    ),

    priority: TaskPriorityEnum | None = None,

    assigned_to: UUID | None = None,

    search: str | None = Query(
        default=None,
        max_length=100,
    ),

    sort_by: str = Query(
        default="created_at",
    ),

    sort_order: str = Query(
        default="desc",
        pattern="^(asc|desc)$",
    ),

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):
    
    await require_project_permission(
        project_id,
        "view_project",
        current_user,
        db,
    )

    tasks, total = await task_crud.get_project_tasks(
        db=db,
        project_id=project_id,
        page=page,
        page_size=page_size,
        status=(
            TaskStatus(status_filter.value)
            if status_filter
            else None
        ),
        priority=(
            TaskPriority(priority.value)
            if priority
            else None
        ),
        assigned_to=assigned_to,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    total_pages = ceil(
        total / page_size
    ) if total else 0

    return TaskListResponse(
        items=tasks,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

@router.patch("/tasks/{task_id}",
    response_model=TaskResponse,
)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    
    task = await task_crud.get_task(
        db,
        task_id,
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    await require_project_permission(
        task.project_id,
        "update_project",
        current_user,
        db,
    )

    return await task_crud.update_task(
        db=db,
        task=task,
        title=data.title,
        description=data.description,
        due_date=data.due_date,
    )
    
@router.delete("/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    
    task = await task_crud.get_task(
        db,
        task_id,
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    await require_project_permission(
        task.project_id,
        "delete_project",
        current_user,
        db,
    )

    await task_crud.delete_task(
        db,
        task,
    )

@router.patch("/tasks/{task_id}/assign",
    response_model=TaskResponse,
)
async def assign_task(
    task_id: UUID,
    data: TaskAssignmentUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    
    task = await task_crud.get_task(
        db,
        task_id,
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    await require_project_permission(
        task.project_id,
        "update_project",
        current_user,
        db,
    )

    if data.assigned_to is not None:

        membership = await get_project_membership(
            db,
            task.project_id,
            data.assigned_to,
        )

        if not membership:
            raise HTTPException(
                status_code=400,
                detail="User is not a member of this project",
            )

    return await task_crud.assign_task(
        db,
        task,
        data.assigned_to,
    )
    
@router.patch("/tasks/{task_id}/status",
    response_model=TaskResponse,
)
async def update_status(
    task_id: UUID,
    data: TaskStatusUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    task = await task_crud.get_task(
        db,
        task_id,
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    await require_project_permission(
        task.project_id,
        "update_project",
        current_user,
        db,
    )

    return await task_crud.update_task_status(
        db,
        task,
        TaskStatus(data.status.value),
    )
    
@router.patch("/tasks/{task_id}/priority",
    response_model=TaskResponse,
)
async def update_priority(
    task_id: UUID,
    data: TaskPriorityUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    task = await task_crud.get_task(
        db,
        task_id,
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    await require_project_permission(
        task.project_id,
        "update_project",
        current_user,
        db,
    )

    return await task_crud.update_task_priority(
        db,
        task,
        TaskPriority(data.priority.value),
    )