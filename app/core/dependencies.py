from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.crud.user import get_user_by_id
from app.database.session import get_db

from app.models.organization_member import (OrganizationMember, OrganizationRole)
from app.crud.organization import get_membership
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(token)
        
        if payload.get("type") != 'access':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token",
                headers={
                  "WWW-Authenticate": "Bearer"  
                },
            )
            
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )
        user_uuid = UUID(user_id)
    except(ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )
    
    user = await get_user_by_id(db, user_uuid)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user
    
def has_permission( role: OrganizationRole, permission: str ) -> bool:

    permissions = {
        OrganizationRole.OWNER: {
            "view_organization",
            "update_organization",
            "delete_organization",
            "view_members",
            "add_member",
            "remove_member",
            "update_member_role"
        },

        OrganizationRole.ADMIN: {
            "view_organization",
            "update_organization",
            "view_members",
            "add_member",
            "remove_member",
            "update_member_role"
        },

        OrganizationRole.MEMBER: {
            "view_organization",
            "view_members"
        }
    }

    return permission in permissions.get(
        role,
        set(),
    )

async def require_organization_permission( organization_id: UUID, permission: str, current_user: User, db: AsyncSession ):
    membership = await get_membership(
        db,
        organization_id,
        current_user.id
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    if not has_permission( membership.role, permission,):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )

    return membership

