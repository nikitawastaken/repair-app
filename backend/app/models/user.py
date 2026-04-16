"""
Модель User (пользователь).
"""
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlmodel import SQLModel, Field
import sqlalchemy as sa
from app.utils import get_current_timestamp


class UserRole(str, Enum):
    """Роли пользователей."""
    CLIENT = "client"
    MASTER = "master"
    ADMIN = "admin"


class User(SQLModel, table=True):
    """Модель пользователя."""
    
    __tablename__ = "user"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    role: UserRole = Field(default=UserRole.CLIENT)
    is_blocked: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=get_current_timestamp,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
