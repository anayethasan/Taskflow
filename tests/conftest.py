
import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from app.main import app
from app.database import Base
from app.database.session import get_db

# Set this environment variable to the dedicated test DB URL.
TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

if not TEST_DATABASE_URL.endswith("/taskflow_test"):
    raise RuntimeError(
        "Tests must use the dedicated taskflow_test database"
    )

test_engine = create_async_engine(TEST_DATABASE_URL)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
)


async def override_get_db():
    async with TestSessionLocal() as db:
        yield db


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    # Import all models so their tables are registered.
    import app.models.user
    import app.models.organization
    import app.models.organization_member
    import app.models.project
    import app.models.project_member
    import app.models.task
    import app.models.notification

    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture
async def client(prepare_database):
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()
