"""
Сервис работы с пользователями.
"""
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import Session

from app.models.user import User, UserRole


async def get_all_users(session: AsyncSession) -> List[User]:
    """Получает всех пользователей (только для админа)."""
    result = await session.execute(select(User))
    return result.scalars().all()


async def update_user_role(
    session: AsyncSession, user: User, new_role: UserRole
) -> User:
    """Обновляет роль пользователя."""
    user.role = new_role
    session.add(user)
    await session.flush()
    return user
