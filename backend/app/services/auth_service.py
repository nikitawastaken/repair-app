"""
Сервис аутентификации.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import Session

from app.config import settings
from app.models.user import User, UserRole
from app.schemas import UserRegister


# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширует пароль."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создаёт JWT токен."""
    to_encode = data.copy()
    
    # Убеждаемся, что 'sub' - это строка
    if "sub" in to_encode and isinstance(to_encode["sub"], int):
        to_encode["sub"] = str(to_encode["sub"])
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm="HS256",
    )
    return encoded_jwt


async def authenticate_user(
    session: AsyncSession, email: str, password: str
) -> Optional[User]:
    """Аутентифицирует пользователя по email и пароль."""
    result = await session.execute(
        select(User).where(User.email == email)
    )
    user = result.scalars().first()
    
    if not user or not verify_password(password, user.hashed_password):
        return None
    
    # Проверяем, не заблокирован ли пользователь
    if user.is_blocked:
        return None
    
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    """Получает пользователя по email."""
    result = await session.execute(
        select(User).where(User.email == email)
    )
    return result.scalars().first()


async def register_user(
    session: AsyncSession, user_data: UserRegister
) -> User:
    """Регистрирует нового пользователя."""
    # Только client и master могут регистрироваться; admin не может быть выбран при регистрации
    role = user_data.role if user_data.role in [UserRole.CLIENT, UserRole.MASTER] else UserRole.CLIENT
    
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),
        role=role,
    )
    session.add(user)
    await session.flush()
    return user
