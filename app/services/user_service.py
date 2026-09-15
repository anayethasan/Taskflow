from sqlalchemy import select
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

async def create_user(db: AsyncSession, user_data: UserCreate,)-> User:
    user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=user_data.hashed_password,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user

async def get_users(db: AsyncSession,) -> list[User]:
    statement = select(User)

    result = await db.execute(statement)

    users = result.scalars().all()

    return users


async def get_user_by_id(db: AsyncSession, user_id: UUID,) -> User | None:
    statement = select(User).where(
        User.id == user_id
    )

    result = await db.execute(statement)

    user = result.scalar_one_or_none()

    return user


async def get_user_by_email(db: AsyncSession, email: str,) -> User | None:
    statement = select(User).where(
        User.email == email
    )

    result = await db.execute(statement)

    user = result.scalar_one_or_none()

    return user


async def update_user(db: AsyncSession, user: User,user_data: UserUpdate,) -> User:
    update_data = user_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return user


async def delete_user(db: AsyncSession, user: User,) -> None:
    await db.delete(user)

    await db.commit()