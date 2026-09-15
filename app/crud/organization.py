from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.organization_member import (
    OrganizationMember,
    OrganizationRole,
)
from app.models.user import User


async def create_organization(db: AsyncSession, name: str, slug: str, user_id: UUID):
    organization = Organization(
        name=name,
        slug=slug
    )

    db.add(organization)

    await db.flush()

    member = OrganizationMember(
        organization_id=organization.id,
        user_id=user_id,
        role=OrganizationRole.OWNER
    )

    db.add(member)

    await db.commit()

    await db.refresh(organization)

    return organization

async def get_organization(db: AsyncSession, organization_id: UUID):
    result = await db.execute(
        select(Organization).where(
            Organization.id == organization_id
        )
    )

    return result.scalar_one_or_none()

async def get_membership(db: AsyncSession, organization_id: UUID, user_id: UUID):
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id
        )
    )

    return result.scalar_one_or_none()

async def get_organization_members( db: AsyncSession, organization_id: UUID,):
    
    result = await db.execute(
        select(OrganizationMember)
        .where(
            OrganizationMember.organization_id
            == organization_id
        )
    )

    return result.scalars().all()

async def get_user_organizations(db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(Organization)
        .join(
            OrganizationMember,
            OrganizationMember.organization_id == Organization.id
        )
        .where(
            OrganizationMember.user_id == user_id
        )
    )

    return result.scalars().all()

