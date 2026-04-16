"""
Pydantic схемы для API запросов и ответов.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole
from app.models.ticket import TicketStatus


# ==================== Auth Schemas ====================

class UserRegister(BaseModel):
    """Схема регистрации пользователя."""
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.CLIENT  # пользователь выбирает роль: client или master


class UserLogin(BaseModel):
    """Схема логина."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Схема ответа с токеном."""
    access_token: str
    token_type: str = "bearer"


# ==================== User Schemas ====================

class UserResponse(BaseModel):
    """Общая схема ответа о пользователе."""
    id: int
    email: str
    full_name: str
    role: UserRole
    is_blocked: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Схема обновления пользователя."""
    full_name: Optional[str] = None


class UserRoleUpdate(BaseModel):
    """Схема изменения роли пользователя."""
    role: UserRole


# ==================== Ticket Schemas ====================

class TicketCreate(BaseModel):
    """Схема создания заявки."""
    title: str
    description: str
    price: float = Field(..., gt=0)  # цена должна быть больше 0
    address: str  # адрес, где нужен ремонт
    category: str  # категория заявки


class TicketStatusUpdate(BaseModel):
    """Схема изменения статуса заявки."""
    status: TicketStatus


class TicketAssign(BaseModel):
    """Схема назначения мастера на заявку."""
    master_id: int


class TicketResponse(BaseModel):
    """Схема ответа о заявке."""
    id: int
    title: str
    description: str
    price: float
    address: str
    category: str
    status: TicketStatus
    client_id: int
    master_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TicketDetailResponse(TicketResponse):
    """Расширенная схема ответа о заявке с данными клиента и мастера."""
    client: UserResponse
    master: Optional[UserResponse] = None
