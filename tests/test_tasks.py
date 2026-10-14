
import pytest


@pytest.mark.asyncio
async def test_tasks_require_authentication(client):
    response = await client.get("/tasks/")

    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_task_requires_authentication(client):
    response = await client.post(
        "/tasks/",
        json={
            "title": "Pytest task",
            "description": "Testing task creation",
            "priority": "medium",
        },
    )

    assert response.status_code in (401, 403)
