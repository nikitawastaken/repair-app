"""
Зависимости для внедрения и проверки прав доступа.
"""
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session
from app.models.user import User, UserRole
from app.services.ticket_service import get_user_by_id


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> User:
    """Получает текущего аутентифицированного пользователя из JWT токена."""
    # Получаем заголовок Authorization
    auth_header = request.headers.get("authorization")
    
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Отсутствует заголовок Authorization",
        )
    
    # Парсим "Bearer <token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный формат заголовка Authorization",
        )
    
    token = parts[1]
    
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"],
        )
        user_id: int = int(payload.get("sub"))
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен",
            )
    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
        )
    
    user = await get_user_by_id(session, user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )

    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь заблокирован",
        )
    
    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Проверяет, что текущий пользователь администратор."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется роль администратор.",
        )
    
    return current_user


async def get_current_master(
    current_user: User = Depends(get_current_user),
) -> User:
    """Проверяет, что текущий пользователь мастер или администратор."""
    if current_user.role not in [UserRole.MASTER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется роль мастер или администратор.",
        )
    
    return current_user


async def get_current_client(
    current_user: User = Depends(get_current_user),
) -> User:
    """Проверяет, что текущий пользователь клиент или администратор."""
    if current_user.role not in [UserRole.CLIENT, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется роль клиент или администратор.",
        )
    
    return current_user
