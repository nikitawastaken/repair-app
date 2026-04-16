"""
Роутер аутентификации.
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session
from app.schemas import UserLogin, UserRegister, Token, UserResponse
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    get_user_by_email,
    register_user,
)
from app.dependencies import get_current_user
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    session: AsyncSession = Depends(get_session),
):
    """Регистрация нового пользователя."""
    # Проверяем, существует ли уже пользователь с такой почтой
    existing_user = await get_user_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )
    
    # Создаём нового пользователя
    user = await register_user(session, user_data)
    await session.commit()
    
    return user


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    session: AsyncSession = Depends(get_session),
):
    """Логин пользователя и получение JWT токена."""
    # Аутентифицируем пользователя
    user = await authenticate_user(session, user_data.email, user_data.password)
    
    if not user:
        # Проверяем, существует ли пользователь, но заблокирован
        existing_user = await get_user_by_email(session, user_data.email)
        if existing_user and existing_user.is_blocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Аккаунт заблокирован",
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный email или пароль",
        )
    
    # Создаём токен
    access_token = create_access_token(data={"sub": user.id})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Получает информацию о текущем авторизованном пользователе."""
    return current_user
