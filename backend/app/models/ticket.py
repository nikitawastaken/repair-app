"""
Модель Ticket (заявка на ремонт).
"""
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlmodel import SQLModel, Field
import sqlalchemy as sa
from app.utils import get_current_timestamp


class TicketStatus(str, Enum):
    """Статусы заявок."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class Ticket(SQLModel, table=True):
    """Модель заявки на ремонт."""
    
    __tablename__ = "ticket"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    price: float  # сумма, которую клиент готов заплатить
    address: str  # адрес, где нужен ремонт
    category: str  # категория (сантехника, электрика, мебель и т.д.)
    status: TicketStatus = Field(default=TicketStatus.NEW)
    client_id: int = Field(foreign_key="user.id")
    master_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(
        default_factory=get_current_timestamp,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=get_current_timestamp,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
