from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.crud.user import create_user, get_user_by_email
from app.database.session import get_db
from app.schemas.auth import RegisterRequest
from app.schemas.user import UserResponse

from app.core.security import (create_access_token, create_refresh_token, verify_password)
from app.schemas.auth import LoginRequest, TokenResponse

from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/register", 
             response_model=UserResponse,
             status_code=status.HTTP_201_CREATED,
             )
async def register(data: RegisterRequest, db: AsyncSession=Depends(get_db)):
    existing_user = await get_user_by_email(
        db,
        data.email,
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    hashed_password = hash_password(
        data.password
    )

    user = await create_user(
        db=db,
        name=data.name,
        email=data.email,
        hashed_password=hashed_password
    )

    return user


@router.post( "/login",
    response_model=TokenResponse,
)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db),):
    user = await get_user_by_email(
        db,
        data.email
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer",
            }
        )

    password_valid = verify_password(
        data.password,
        user.hashed_password,
    )

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer",
            }
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    access_token = create_access_token(
        user.id,
    )

    refresh_token = create_refresh_token(
        user.id,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )
    
@router.get("/me",
            response_model=UserResponse,
            )
async def get_me(current_user=Depends(get_current_user)):
    return current_user