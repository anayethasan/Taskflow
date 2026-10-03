from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.project_member import ProjectMember, ProjectRole


async def get_project( db: AsyncSession, project_id: UUID, ):
    result = await db.execute(
        select(Project).where(
            Project.id == project_id
        )
    )

    return result.scalar_one_or_none()

async def create_project( db: AsyncSession, organization_id: UUID, user_id: UUID, name: str, slug: str, description: str | None = None, ):
    project = Project(
        organization_id=organization_id,
        name=name,
        slug=slug,
        description=description,
        created_by=user_id,
    )

    db.add(project)

    await db.flush()

    owner = ProjectMember(
        project_id=project.id,
        user_id=user_id,
        role=ProjectRole.OWNER,
    )

    db.add(owner)

    await db.commit()

    await db.refresh(project)

    return project

async def get_projects_by_organization( db: AsyncSession, organization_id: UUID, ):
    result = await db.execute(
        select(Project)
        .where(
            Project.organization_id == organization_id
        )
        .order_by(Project.created_at.desc())
    )

    return result.scalars().all()

async def update_project( db: AsyncSession, project: Project, name: str | None = None, description: str | None = None, ):
    if name is not None:
        project.name = name

    if description is not None:
        project.description = description

    await db.commit()

    await db.refresh(project)

    return project

async def delete_project( db: AsyncSession, project: Project, ):
    await db.delete(project)

    await db.commit()
    
async def get_project_membership( db: AsyncSession, project_id: UUID, user_id: UUID, ):
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )

    return result.scalar_one_or_none()

async def get_project_members( db: AsyncSession, project_id: UUID, ):
    result = await db.execute(
        select(ProjectMember)
        .where(
            ProjectMember.project_id == project_id
        )
        .order_by(ProjectMember.created_at)
    )

    return result.scalars().all()

async def add_project_member( db: AsyncSession, project_id: UUID, user_id: UUID, role: ProjectRole = ProjectRole.MEMBER, ):
    
    member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=role,
    )

    db.add(member)

    await db.commit()

    await db.refresh(member)

    return member

async def update_project_member_role( db: AsyncSession, member: ProjectMember, role: ProjectRole, ):
    member.role = role

    await db.commit()

    await db.refresh(member)

    return member

async def remove_project_member( db: AsyncSession, member: ProjectMember, ):
    await db.delete(member)

    await db.commit()