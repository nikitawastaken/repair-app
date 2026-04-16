"""
Роутер заявок (мастерская площадка).
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies import get_current_user, get_current_client, get_current_master
from app.models.user import User, UserRole
from app.models.ticket import TicketStatus
from app.schemas import TicketCreate, TicketResponse
from app.services.ticket_service import (
    create_ticket,
    get_all_tickets,
    get_ticket_by_id,
    get_tickets_for_client,
    get_open_tickets,
    take_ticket,
    abandon_ticket,
    complete_ticket,
    cancel_ticket,
    search_and_filter_tickets,
)


router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketResponse])
async def list_tickets(
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    search: Optional[str] = Query(None, description="Поиск по названию и описанию"),
    min_price: Optional[float] = Query(None, ge=0, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, ge=0, description="Максимальная цена"),
    sort_by: str = Query("created_at", description="Сортировка: created_at или price"),
    order: str = Query("desc", description="Порядок: asc или desc"),
    my_tickets: bool = Query(False, description="Показать только свои заявки (для мастеров)"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Получить список заявок в зависимости от роли и фильтров:
    - client: только свои заявки
    - master: открытые заявки (статус new) или свои заявки (my_tickets=true)
    - admin: все заявки
    """
    # Преобразуем статус в enum если задан
    status_enum = None
    if status:
        try:
            status_enum = TicketStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Недопустимый статус: {status}",
            )
    
    if current_user.role == UserRole.CLIENT:
        # Клиент видит только свои заявки
        tickets = await get_tickets_for_client(session, current_user.id)
        return tickets
    
    elif current_user.role == UserRole.MASTER:
        # Если мастер запрашивает свои заявки (my_tickets=true)
        if my_tickets:
            tickets = await search_and_filter_tickets(
                session,
                master_id=current_user.id,
                status=status_enum,
                category=category,
                search=search,
                min_price=min_price,
                max_price=max_price,
                sort_by=sort_by,
                order=order,
            )
        else:
            # Мастер видит открытые заявки с фильтрацией
            # По умолчанию показываем только new если статус не указан
            if not status_enum:
                status_enum = TicketStatus.NEW
            
            tickets = await search_and_filter_tickets(
                session,
                status=status_enum,
                category=category,
                search=search,
                min_price=min_price,
                max_price=max_price,
                sort_by=sort_by,
                order=order,
            )
        return tickets
    
    else:  # ADMIN
        # Админ видит все заявки с фильтрацией
        tickets = await search_and_filter_tickets(
            session,
            status=status_enum,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            order=order,
        )
        return tickets


@router.post("", response_model=TicketResponse)
async def create_new_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_client),
    session: AsyncSession = Depends(get_session),
):
    """Создать новую заявку (доступно только для клиентов)."""
    # Валидация данных (дополнительная, так как pydantic уже валидирует)
    if not ticket_data.title or not ticket_data.title.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Название заявки не может быть пустым",
        )
    
    if not ticket_data.description or not ticket_data.description.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Описание заявки не может быть пустым",
        )
    
    if ticket_data.price <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Цена должна быть больше нуля",
        )
    
    ticket = await create_ticket(session, current_user.id, ticket_data)
    await session.commit()
    
    return ticket


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Получить детали заявки."""
    ticket = await get_ticket_by_id(session, ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена",
        )
    
    # Проверяем права доступа
    can_view = False
    
    if current_user.role == UserRole.ADMIN:
        can_view = True
    elif current_user.role == UserRole.CLIENT and ticket.client_id == current_user.id:
        can_view = True
    elif current_user.role == UserRole.MASTER and ticket.master_id == current_user.id:
        can_view = True
    
    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на просмотр этой заявки",
        )
    
    return ticket


@router.patch("/{ticket_id}/take", response_model=TicketResponse)
async def take_ticket_endpoint(
    ticket_id: int,
    current_user: User = Depends(get_current_master),
    session: AsyncSession = Depends(get_session),
):
    """Мастер берёт заявку в работу (new → in_progress)."""
    ticket = await get_ticket_by_id(session, ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена",
        )
    
    # Проверяем статус заявки
    if ticket.status != TicketStatus.NEW:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Заявка уже взята другим мастером или выполнена",
        )
    
    # Берём заявку
    result = await take_ticket(session, ticket, current_user.id)
    await session.commit()
    
    return result


@router.patch("/{ticket_id}/abandon", response_model=TicketResponse)
async def abandon_ticket_endpoint(
    ticket_id: int,
    current_user: User = Depends(get_current_master),
    session: AsyncSession = Depends(get_session),
):
    """Мастер отказывается от заявки (in_progress → new)."""
    ticket = await get_ticket_by_id(session, ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена",
        )
    
    # Проверяем, что это заявка мастера и она в работе
    if ticket.master_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Это не ваша заявка",
        )
    
    if ticket.status != TicketStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно отказаться только от заявок в работе",
        )
    
    # Отказываемся от заявки
    result = await abandon_ticket(session, ticket)
    await session.commit()
    
    return result


@router.patch("/{ticket_id}/done", response_model=TicketResponse)
async def complete_ticket_endpoint(
    ticket_id: int,
    current_user: User = Depends(get_current_master),
    session: AsyncSession = Depends(get_session),
):
    """Мастер завершает заявку (in_progress → done)."""
    ticket = await get_ticket_by_id(session, ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена",
        )
    
    # Проверяем, что это заявка мастера и она в работе
    if ticket.master_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Это не ваша заявка",
        )
    
    if ticket.status != TicketStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно завершить только заявки в работе",
        )
    
    # Завершаем заявку
    result = await complete_ticket(session, ticket)
    await session.commit()
    
    return result


@router.patch("/{ticket_id}/cancel", response_model=TicketResponse)
async def cancel_ticket_endpoint(
    ticket_id: int,
    current_user: User = Depends(get_current_client),
    session: AsyncSession = Depends(get_session),
):
    """Клиент отзывает заявку (new → cancelled)."""
    ticket = await get_ticket_by_id(session, ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена",
        )
    
    # Проверяем, что это заявка клиента
    if ticket.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Это не ваша заявка",
        )
    
    # Проверяем статус
    if ticket.status != TicketStatus.NEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно отозвать только новые заявки",
        )
    
    # Отзываем заявку
    result = await cancel_ticket(session, ticket)
    await session.commit()
    
    return result
