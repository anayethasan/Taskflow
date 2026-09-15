from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrganizationCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100
    )


class OrganizationUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationRoleEnum(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class AddMemberRequest(BaseModel):
    email: EmailStr


class UpdateMemberRoleRequest(BaseModel):
    role: OrganizationRoleEnum


class MemberResponse(BaseModel):
    id: UUID
    user_id: UUID
    role: OrganizationRoleEnum
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)