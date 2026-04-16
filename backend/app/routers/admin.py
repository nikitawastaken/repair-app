"""
Роутер администратора.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies import get_current_admin
from app.models.user import User
from app.schemas import TicketResponse, UserResponse
from app.services.ticket_service import (
    delete_ticket,
    get_all_tickets,
    get_ticket_by_id,
    get_all_users,
    block_user,
    unblock_user,
    get_user_by_id,
)


router = APIRouter(prefix="/admin", tags=["admin"])


# ==================== Tickets (админ-функции) ====================

@router.get("/tickets", response_model=list[TicketResponse])
async def get_all_tickets_admin(
    current_user: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    """Получить все заявки (администратор)."""
    tickets = await get_all_tickets(session)
    return tickets


@router.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket_admin(
    ticket_id: int,
    current_user: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    """Удалить заявку (администратор)."""
    ticket = await get_ticket_by_id(session, ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена",
        )
    
    await delete_ticket(session, ticket)
    await session.commit()


# ==================== Users (админ-функции) ====================

@router.get("/users", response_model=list[UserResponse])
async def get_all_users_admin(
    current_user: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    """Получить всех пользователей (администратор)."""
    users = await get_all_users(session)
    return users


@router.patch("/users/{user_id}/block", response_model=UserResponse)
async def block_user_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    """Заблокировать / разблокировать пользователя (администратор)."""
    user = await get_user_by_id(session, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    
    # Нельзя заблокировать себя
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя заблокировать собственный аккаунт",
        )
    
    if user.is_blocked:
        # Уже заблокирован, разблокировать
        result = await unblock_user(session, user)
    else:
        # Заблокировать
        result = await block_user(session, user)
    
    await session.commit()
    return result
