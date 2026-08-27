import uuid
from sqlalchemy import UUID as SQLUUID

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    
    name: Mapped[str] = mapped_column(
        String(100),
    )
    
    email: Mapped[str] = mapped_column(
        String(250),
        unique=True,
        index=True,
    )
    
    hashed_password: Mapped[str] = mapped_column(
        String(275),
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )