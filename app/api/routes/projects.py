from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_current_user,
    require_organization_permission,
    require_project_permission,
)
from app.crud import project as project_crud
from app.crud.user import get_user_by_email
from app.database.session import get_db
from app.models.project_member import ProjectRole
from app.models.user import User
from app.schemas.project import (AddProjectMemberRequest, ProjectCreate, ProjectMemberResponse, ProjectResponse, ProjectRoleEnum, ProjectUpdate, UpdateProjectMemberRoleRequest,)
from app.core.utils import generate_slug


from app.core.cache import (
    delete_cache,
    get_cache,
    set_cache,
)

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)

@router.post("/organizations/{organization_id}/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(organization_id: UUID, data: ProjectCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),):
    
    await require_organization_permission(
        organization_id,
        "update_organization",
        current_user,
        db,
    )

    slug = generate_slug(data.name)

    project = await project_crud.create_project(
        db=db,
        organization_id=organization_id,
        user_id=current_user.id,
        name=data.name,
        slug=slug,
        description=data.description,
    )

    return project


# @router.get("/{project_id}",
#     response_model=ProjectResponse,
# )
# async def get_project(project_id: UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),):
    
#     await require_project_permission(
#         project_id,
#         "view_project",
#         current_user,
#         db,
#     )

#     project = await project_crud.get_project(
#         db,
#         project_id,
#     )

#     if not project:
#         raise HTTPException(
#             status_code=404,
#             detail="Project not found",
#         )

#     return project

@router.get("/{project_id}",
    response_model=ProjectResponse,
)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project, membership = await require_project_permission(
        project_id=project_id,
        permission="view_project",
        current_user=current_user,
        db=db,
    )

    cache_key = f"project:{project_id}"

    cached_project = await get_cache(cache_key)

    if cached_project is not None:
        return cached_project

    response = ProjectResponse.model_validate(project)

    await set_cache(
        cache_key,
        response.model_dump(mode="json"),
        expire=300,
    )

    return response

@router.get("/organizations/{organization_id}/projects",
    response_model=list[ProjectResponse],
)
async def list_projects(organization_id: UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),):
    
    await require_organization_permission(
        organization_id,
        "view_organization",
        current_user,
        db,
    )

    return await project_crud.get_projects_by_organization(
        db,
        organization_id,
    )
    
@router.patch("/{project_id}",
    response_model=ProjectResponse,
)
async def update_project(project_id: UUID, data: ProjectUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),):
    project, _ = await require_project_permission(
        project_id,
        "update_project",
        current_user,
        db,
    )

    return await project_crud.update_project(
        db=db,
        project=project,
        name=data.name,
        description=data.description,
    )
    
@router.delete("/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project(project_id: UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),):
    
    project, _ = await require_project_permission(
        project_id,
        "delete_project",
        current_user,
        db,
    )

    await project_crud.delete_project(
        db,
        project,
    )
    
@router.post("/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_project_member(project_id: UUID, data: AddProjectMemberRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),):
    
    await require_project_permission(
        project_id,
        "add_member",
        current_user,
        db,
    )

    user = await get_user_by_email(
        db,
        data.email,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    existing = await project_crud.get_project_membership(
        db,
        project_id,
        user.id,
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="User is already a project member",
        )

    return await project_crud.add_project_member(
        db=db,
        project_id=project_id,
        user_id=user.id,
    )
    

@router.get("/{project_id}/members",
    response_model=list[ProjectMemberResponse],
)
async def list_project_members(project_id: UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),):
    
    await require_project_permission(
        project_id,
        "view_members",
        current_user,
        db,
    )

    return await project_crud.get_project_members(
        db,
        project_id,
    )
    
@router.patch("/{project_id}/members/{user_id}",
    response_model=ProjectMemberResponse,
)
async def update_project_member_role(
    project_id: UUID,
    user_id: UUID,
    data: UpdateProjectMemberRoleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_project_permission(
        project_id,
        "update_member_role",
        current_user,
        db,
    )

    member = await project_crud.get_project_membership(
        db,
        project_id,
        user_id,
    )

    if not member:
        raise HTTPException(
            status_code=404,
            detail="Project member not found",
        )

    if member.role == ProjectRole.OWNER:
        raise HTTPException(
            status_code=400,
            detail="Project owner role cannot be changed",
        )

    new_role = ProjectRole(data.role.value)

    if new_role == ProjectRole.OWNER:
        raise HTTPException(
            status_code=400,
            detail="Owner role cannot be assigned this way",
        )

    return await project_crud.update_project_member_role(
        db,
        member,
        new_role,
    )
    
@router.delete("/{project_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_project_member(
    project_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_project_permission(
        project_id,
        "remove_member",
        current_user,
        db,
    )

    member = await project_crud.get_project_membership(
        db,
        project_id,
        user_id,
    )

    if not member:
        raise HTTPException(
            status_code=404,
            detail="Project member not found",
        )

    if member.role == ProjectRole.OWNER:
        raise HTTPException(
            status_code=400,
            detail="Project owner cannot be removed",
        )

    await project_crud.remove_project_member(
        db,
        member,
    )
    
