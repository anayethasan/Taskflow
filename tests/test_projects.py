
import pytest


@pytest.mark.asyncio
async def test_projects_require_authentication(client):
    response = await client.get("/projects/")

    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_project_requires_authentication(client):
    response = await client.post(
        "/projects/",
        json={
            "name": "Pytest Project",
            "slug": "pytest-project",
            "description": "Created during testing",
        },
    )

    assert response.status_code in (401, 403)
