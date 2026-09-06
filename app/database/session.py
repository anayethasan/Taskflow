# from collections.abc import Generator
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# from app.core.config import settings

# engine = create_engine(
#     settings.DATABASE_URL,
#     echo=settings.DEBUG,
# )

# SessionLocal = sessionmaker(
#     bind=engine,
#     autoflush=False,
#     autocommit=False,
# )


# def get_db() -> Generator:
#     db = SessionLocal()
    
#     try:
#         yield db
#     finally:
#         db.close()
        
        
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        yield db