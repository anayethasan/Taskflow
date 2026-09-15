from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_organization_permission
from app.core.utils import generate_slug
from app.crud.organization import (
    create_organization,
    get_membership,
    get_organization,
    get_organization_members,
    get_user_organizations
)
from app.crud.user import get_user_by_email
from app.database.session import get_db
from app.models.organization_member import (
    OrganizationMember,
    OrganizationRole,
)
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    AddMemberRequest,
    MemberResponse,
    UpdateMemberRoleRequest,
)

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)

@router.post("/",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_organization_route(data: OrganizationCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    slug = generate_slug(data.name)

    organization = await create_organization(
        db=db,
        name=data.name,
        slug=slug,
        user_id=current_user.id
    )

    return organization

@router.get("/",
    response_model=list[OrganizationResponse],
)
async def get_my_organizations(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    organizations = await get_user_organizations(
        db,
        current_user.id
    )

    return organizations

@router.get("/{organization_id}",
    response_model=OrganizationResponse,
)
async def get_organization_route(organization_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    membership = await get_membership(
        db,
        organization_id,
        current_user.id
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    organization = await get_organization(
        db,
        organization_id
    )

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    return organization

@router.patch( "/{organization_id}",
    response_model=OrganizationResponse,
)
async def update_organization( organization_id: UUID, data: OrganizationUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),):
    await require_organization_permission(
        organization_id,
        "update_organization",
        current_user,
        db,
    )

    organization = await get_organization(
        db,
        organization_id,
    )

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    if data.name is not None:
        organization.name = data.name
        organization.slug = generate_slug(data.name)

    await db.commit()
    await db.refresh(organization)

    return organization

@router.delete("/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_organization( organization_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),):
    
    membership = await require_organization_permission(
        organization_id,
        "delete_organization",
        current_user,
        db,
    )

    organization = await get_organization(
        db,
        organization_id,
    )

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    await db.delete(organization)
    await db.commit()

    return None

@router.post("/{organization_id}/members",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_member( organization_id: UUID, data: AddMemberRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), ):
    
    await require_organization_permission(
        organization_id,
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

    existing_member = await get_membership(
        db,
        organization_id,
        user.id,
    )

    if existing_member:
        raise HTTPException(
            status_code=409,
            detail="User is already a member",
        )

    member = OrganizationMember(
        organization_id=organization_id,
        user_id=user.id,
        role=OrganizationRole.MEMBER,
    )

    db.add(member)

    await db.commit()
    await db.refresh(member)

    return member


@router.get("/{organization_id}/members",
    response_model=list[MemberResponse],
)
async def list_members( organization_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), ):
    await require_organization_permission(
        organization_id,
        "view_members",
        current_user,
        db
    )

    return await get_organization_members( db, organization_id, )


@router.delete("/{organization_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_member( organization_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), ):
    
    await require_organization_permission(
        organization_id,
        "remove_member",
        current_user,
        db,
    )

    member = await get_membership(
        db,
        organization_id,
        user_id,
    )

    if not member:
        raise HTTPException(
            status_code=404,
            detail="Member not found",
        )

    if member.role == OrganizationRole.OWNER:
        raise HTTPException(
            status_code=400,
            detail="Organization owner cannot be removed",
        )

    await db.delete(member)
    await db.commit()

    return None

@router.patch("/{organization_id}/members/{user_id}",
    response_model=MemberResponse,
)
async def update_member_role( organization_id: UUID, user_id: UUID, data: UpdateMemberRoleRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),):
    
    await require_organization_permission(
        organization_id,
        "update_member_role",
        current_user,
        db,
    )

    member = await get_membership(
        db,
        organization_id,
        user_id,
    )

    if not member:
        raise HTTPException(
            status_code=404,
            detail="Member not found",
        )

    if member.role == OrganizationRole.OWNER:
        raise HTTPException(
            status_code=400,
            detail="Owner role cannot be changed here",
        )

    if data.role == OrganizationRole.OWNER:
        raise HTTPException(
            status_code=400,
            detail="Owner role cannot be assigned here",
        )

    member.role = data.role

    await db.commit()
    await db.refresh(member)

    return member
