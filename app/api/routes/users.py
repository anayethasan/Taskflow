from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.user import (UserCreate, UserResponse, UserUpdate,)

from app.services import user_service

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def user_create(user_data: UserCreate, db:Session=Depends(get_db)):
    existing_user = user_service.get_user_by_email(
        db,
        user_data.email,
    )
    
    if(existing_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    user = user_service.create_user(
        db,
        user_data,    
    )
    return user


@router.get(
    "/",
    response_model=list[UserResponse],
)
def get_users(db: Session = Depends(get_db),):
    users = user_service.get_users(db)

    return users

@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(user_id: int, db: Session = Depends(get_db),):
    user = user_service.get_user_by_id(
        db,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db),):
    user = user_service.get_user_by_id(
        db,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user_data.email:
        existing_user = user_service.get_user_by_email(
            db,
            user_data.email,
        )

        if existing_user and existing_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    updated_user = user_service.update_user(
        db,
        user,
        user_data,
    )

    return updated_user

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(user_id: int, db: Session = Depends(get_db),):
    user = user_service.get_user_by_id(
        db,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user_service.delete_user(
        db,
        user,
    )