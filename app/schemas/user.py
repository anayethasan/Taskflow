from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    hashed_password: str
    
class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    
class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)