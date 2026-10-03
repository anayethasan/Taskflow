from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskStatusEnum(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    assigned_to: UUID | None = None

    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM

    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    due_date: datetime | None = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatusEnum


class TaskPriorityUpdate(BaseModel):
    priority: TaskPriorityEnum


class TaskAssignmentUpdate(BaseModel):
    assigned_to: UUID | None = None


class TaskResponse(BaseModel):
    id: UUID
    project_id: UUID
    created_by: UUID
    assigned_to: UUID | None

    title: str
    description: str | None

    status: TaskStatusEnum
    priority: TaskPriorityEnum

    due_date: datetime | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )

class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int