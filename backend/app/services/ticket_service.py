"""
Сервис работы с заявками (мастерская площадка).
"""
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.ticket import Ticket, TicketStatus
from app.models.user import User, UserRole


async def create_ticket(
    session: AsyncSession, client_id: int, ticket_data
) -> Ticket:
    """Создаёт новую заявку."""
    ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        price=ticket_data.price,
        address=ticket_data.address,
        category=ticket_data.category,
        client_id=client_id,
    )
    session.add(ticket)
    await session.flush()
    return ticket


async def get_ticket_by_id(
    session: AsyncSession, ticket_id: int
) -> Optional[Ticket]:
    """Получает заявку по ID."""
    result = await session.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    return result.scalars().first()


async def get_tickets_for_client(
    session: AsyncSession, client_id: int
) -> List[Ticket]:
    """Получает все заявки клиента."""
    result = await session.execute(
        select(Ticket).where(Ticket.client_id == client_id)
    )
    return result.scalars().all()


async def get_tickets_for_master(
    session: AsyncSession, master_id: int
) -> List[Ticket]:
    """Получает заявки мастера (назначенные ему)."""
    result = await session.execute(
        select(Ticket).where(Ticket.master_id == master_id)
    )
    return result.scalars().all()


async def get_all_tickets(session: AsyncSession) -> List[Ticket]:
    """Получает все заявки (только для админа)."""
    result = await session.execute(select(Ticket))
    return result.scalars().all()


async def get_open_tickets(session: AsyncSession) -> List[Ticket]:
    """Получает все открытые заявки (статус new) для доски мастера."""
    result = await session.execute(
        select(Ticket).where(Ticket.status == TicketStatus.NEW)
    )
    return result.scalars().all()


async def take_ticket(
    session: AsyncSession,
    ticket: Ticket,
    master_id: int,
) -> Ticket:
    """Мастер берёт заявку в работу (new → in_progress)."""
    # Проверяем, что заявка в статусе new
    if ticket.status != TicketStatus.NEW:
        return None  # Ошибка — заявка уже взята или в другом статусе
    
    ticket.status = TicketStatus.IN_PROGRESS
    ticket.master_id = master_id
    ticket.updated_at = datetime.now(timezone.utc)
    session.add(ticket)
    await session.flush()
    return ticket


async def abandon_ticket(
    session: AsyncSession,
    ticket: Ticket,
) -> Ticket:
    """Мастер отказывается от заявки (in_progress → new)."""
    # Проверяем, что заявка в статусе in_progress
    if ticket.status != TicketStatus.IN_PROGRESS:
        return None
    
    ticket.status = TicketStatus.NEW
    ticket.master_id = None
    ticket.updated_at = datetime.now(timezone.utc)
    session.add(ticket)
    await session.flush()
    return ticket


async def complete_ticket(
    session: AsyncSession,
    ticket: Ticket,
) -> Ticket:
    """Мастер завершает заявку (in_progress → done)."""
    # Проверяем, что заявка в статусе in_progress
    if ticket.status != TicketStatus.IN_PROGRESS:
        return None
    
    ticket.status = TicketStatus.DONE
    ticket.updated_at = datetime.now(timezone.utc)
    session.add(ticket)
    await session.flush()
    return ticket


async def cancel_ticket(
    session: AsyncSession,
    ticket: Ticket,
) -> Ticket:
    """Клиент отзывает заявку (new → cancelled)."""
    # Проверяем, что заявка в статусе new
    if ticket.status != TicketStatus.NEW:
        return None
    
    ticket.status = TicketStatus.CANCELLED
    ticket.updated_at = datetime.now(timezone.utc)
    session.add(ticket)
    await session.flush()
    return ticket


async def delete_ticket(
    session: AsyncSession,
    ticket: Ticket,
) -> bool:
    """Администратор удаляет заявку."""
    await session.delete(ticket)
    await session.flush()
    return True


async def search_and_filter_tickets(
    session: AsyncSession,
    status: Optional[TicketStatus] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "created_at",
    order: str = "desc",
    master_id: Optional[int] = None,
) -> List[Ticket]:
    """Поиск и фильтрация заявок."""
    query = select(Ticket)
    
    # Фильтр по мастеру
    if master_id is not None:
        query = query.where(Ticket.master_id == master_id)
    
    # Фильтр по статусу
    if status:
        query = query.where(Ticket.status == status)
    
    # Фильтр по категории
    if category:
        query = query.where(Ticket.category == category)
    
    # Поиск по названию и описанию (case-insensitive)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Ticket.title.ilike(search_pattern)) |
            (Ticket.description.ilike(search_pattern))
        )
    
    # Фильтр по цене
    if min_price is not None:
        query = query.where(Ticket.price >= min_price)
    
    if max_price is not None:
        query = query.where(Ticket.price <= max_price)
    
    # Сортировка
    if sort_by == "price":
        sort_column = Ticket.price
    else:  # created_at
        sort_column = Ticket.created_at
    
    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    result = await session.execute(query)
    return result.scalars().all()


async def get_user_by_id(
    session: AsyncSession, user_id: int
) -> Optional[User]:
    """Получает пользователя по ID."""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalars().first()


async def get_all_users(session: AsyncSession) -> List[User]:
    """Получает всех пользователей (для админа)."""
    result = await session.execute(select(User))
    return result.scalars().all()


async def block_user(
    session: AsyncSession,
    user: User,
) -> User:
    """Администратор блокирует пользователя."""
    user.is_blocked = True
    session.add(user)
    await session.flush()
    return user


async def unblock_user(
    session: AsyncSession,
    user: User,
) -> User:
    """Администратор разблокирует пользователя."""
    user.is_blocked = False
    session.add(user)
    await session.flush()
    return user
