from fastapi import APIRouter, HTTPException
import httpx

from app.services.external_api import fetch_external_user

router = APIRouter(
    prefix="/external",
    tags=["External API"],
)


@router.get("/users/{user_id}")
async def get_external_user(user_id: int):
    if user_id < 1:
        raise HTTPException(
            status_code=422,
            detail="User ID must be greater than zero",
        )

    try:
        user = await fetch_external_user(user_id)
        return user

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="External API timed out",
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="External API returned an error",
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to external API",
        )