
import pytest


@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/auth/register",
        json={
            "email": "pytest_user@example.com",
            "password": "StrongPass123!",
        },
    )

    assert response.status_code in (200, 201)


@pytest.mark.asyncio
async def test_login_user(client):
    # Register first so this test does not depend on
    # a user created by another test.
    await client.post(
        "/auth/register",
        json={
            "email": "login_user@example.com",
            "password": "StrongPass123!",
        },
    )

    response = await client.post(
        "/auth/login",
        data={
            "username": "login_user@example.com",
            "password": "StrongPass123!",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"].lower() == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    response = await client.post(
        "/auth/login",
        data={
            "username": "unknown@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code in (400, 401)


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client):
    response = await client.get("/users/me")

    assert response.status_code in (401, 403)
