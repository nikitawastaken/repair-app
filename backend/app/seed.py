"""
Скрипт для заполнения БД начальными данными.
Идемпотентный (повторный запуск не создаёт дубликаты).
"""
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import Session

from app.database import async_session_maker
from app.models.user import User, UserRole
from app.models.ticket import Ticket, TicketStatus
from app.services.auth_service import hash_password


async def seed_database():
    """Заполняет БД начальными данными."""
    async with async_session_maker() as session:
        # ==================== Создание пользователей ====================
        
        # Проверяем, существуют ли уже пользователи
        result = await session.execute(select(User))
        existing_users = result.scalars().all()
        
        if existing_users:
            print("❌ БД уже содержит пользователей. Seed не выполнен.")
            return
        
        # Создаём пользователей
        users_data = [
            {
                "email": "admin@repair.ru",
                "full_name": "Администратор",
                "password": "Admin1234!",
                "role": UserRole.ADMIN,
            },
            {
                "email": "master1@repair.ru",
                "full_name": "Мастер Иван Сидоров",
                "password": "Master123!",
                "role": UserRole.MASTER,
            },
            {
                "email": "master2@repair.ru",
                "full_name": "Мастер Петр Волков",
                "password": "Master123!",
                "role": UserRole.MASTER,
            },
            {
                "email": "client1@repair.ru",
                "full_name": "Клиент Игорь Морозов",
                "password": "Client123!",
                "role": UserRole.CLIENT,
            },
            {
                "email": "client2@repair.ru",
                "full_name": "Клиентка Мария Федорова",
                "password": "Client123!",
                "role": UserRole.CLIENT,
            },
        ]
        
        users = {}
        for user_data in users_data:
            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=hash_password(user_data["password"]),
                role=user_data["role"],
                is_blocked=False,
            )
            session.add(user)
            users[user_data["email"]] = user
        
        await session.flush()
        
        print("✅ Пользователи созданы:")
        for user_data in users_data:
            print(f"   - {user_data['email']} ({user_data['role'].value}) / пароль: {user_data['password']}")
        
        # ==================== Создание заявок ====================
        
        client1 = users["client1@repair.ru"]
        client2 = users["client2@repair.ru"]
        master1 = users["master1@repair.ru"]
        master2 = users["master2@repair.ru"]
        
        tickets_data = [
            # Заявки со статусом NEW (без мастера) - 5 штук
            {
                "title": "Сломан холодильник",
                "description": "Холодильник не включается. На двери есть лёд. Нужна срочная помощь.",
                "price": 2500.0,
                "address": "ул. Ленина, 45, кв. 12",
                "category": "Бытовая техника",
                "status": TicketStatus.NEW,
                "client_id": client1.id,
                "master_id": None,
            },
            {
                "title": "Протечка в ванной",
                "description": "Вода течёт из крана, не закрывается нормально. Срочно требуется ремонт.",
                "price": 1800.0,
                "address": "пр. Мира, 23, кв. 5",
                "category": "Сантехника",
                "status": TicketStatus.NEW,
                "client_id": client2.id,
                "master_id": None,
            },
            {
                "title": "Нет электричества в комнате",
                "description": "Правая розетка не работает. Перебоев света не было. Возможно, проблема с проводкой.",
                "price": 1200.0,
                "address": "ул. Кирова, 78, кв. 3",
                "category": "Электрика",
                "status": TicketStatus.NEW,
                "client_id": client1.id,
                "master_id": None,
            },
            {
                "title": "Поклейка обоев",
                "description": "Нужно переклеить обои в комнате. Размер примерно 4х5м. Старые обои надо снять.",
                "price": 3500.0,
                "address": "ул. Пушкина, 34, кв. 8",
                "category": "Отделка",
                "status": TicketStatus.NEW,
                "client_id": client2.id,
                "master_id": None,
            },
            {
                "title": "Микроволновка не работает",
                "description": "Микроволновка перестала работать. Панель светится, но не греет. Куплена 3 года назад.",
                "price": 2000.0,
                "address": "ул. Октябрьская, 56, кв. 10",
                "category": "Бытовая техника",
                "status": TicketStatus.NEW,
                "client_id": client1.id,
                "master_id": None,
            },
            
            # Заявки со статусом IN_PROGRESS - 4 штуки
            {
                "title": "Установка полки",
                "description": "Нужно установить деревянную полку на стену в гостиной. Крепёж предоставлен.",
                "price": 800.0,
                "address": "ул. Советская, 12, кв. 2",
                "category": "Мебель",
                "status": TicketStatus.IN_PROGRESS,
                "client_id": client1.id,
                "master_id": master1.id,
            },
            {
                "title": "Замена смесителя",
                "description": "Нужно заменить смеситель на кухне. Новый смеситель есть дома. Старый нужно снять.",
                "price": 1500.0,
                "address": "пр. Ленина, 99, кв. 7",
                "category": "Сантехника",
                "status": TicketStatus.IN_PROGRESS,
                "client_id": client2.id,
                "master_id": master2.id,
            },
            {
                "title": "Видеонаблюдение в офисе",
                "description": "Установка видеокамер и записывающего устройства. 4 камеры на улице и 2 внутри.",
                "price": 15000.0,
                "address": "ул. Торговая, 45",
                "category": "Электрика",
                "status": TicketStatus.IN_PROGRESS,
                "client_id": client1.id,
                "master_id": master1.id,
            },
            {
                "title": "Ремонт входной двери",
                "description": "Заклинила входная дверь. Крепёж ослаб и нужна регулировка.",
                "price": 2000.0,
                "address": "ул. Фрунзе, 67, кв. 11",
                "category": "Мебель",
                "status": TicketStatus.IN_PROGRESS,
                "client_id": client2.id,
                "master_id": master2.id,
            },
            
            # Заявки со статусом DONE - 4 штуки
            {
                "title": "Замена люстры",
                "description": "Установлена новая люстра с встроенными светодиодами. Старая люстра снята и утилизирована.",
                "price": 3500.0,
                "address": "ул. Красная, 23, кв. 6",
                "category": "Электрика",
                "status": TicketStatus.DONE,
                "client_id": client1.id,
                "master_id": master1.id,
            },
            {
                "title": "Герметизация окон",
                "description": "Выполнена герметизация щелей в окнах. Убран конденсат и улучшена теплоизоляция.",
                "price": 2200.0,
                "address": "ул. Космонавтов, 89, кв. 4",
                "category": "Отделка",
                "status": TicketStatus.DONE,
                "client_id": client2.id,
                "master_id": master2.id,
            },
            {
                "title": "Установка кондиционера",
                "description": "Выполнена профессиональная установка сплит-системы кондиционирования с гарантией.",
                "price": 8000.0,
                "address": "ул. Авиаторов, 15, кв. 9",
                "category": "Бытовая техника",
                "status": TicketStatus.DONE,
                "client_id": client1.id,
                "master_id": master1.id,
            },
            {
                "title": "Облицовка плиткой",
                "description": "Уложена керамическая плитка в ванной комнате площадью 8 м².",
                "price": 6000.0,
                "address": "ул. Нагорная, 42, кв. 1",
                "category": "Отделка",
                "status": TicketStatus.DONE,
                "client_id": client2.id,
                "master_id": master2.id,
            },
            
            # Заявки со статусом CANCELLED - 2 штуки
            {
                "title": "Покраска стен (ОТМЕНЕНО)",
                "description": "Заявка была создана, но затем отменена клиентом - решил покрасить сам.",
                "price": 2500.0,
                "address": "ул. Березовая, 11, кв. 3",
                "category": "Отделка",
                "status": TicketStatus.CANCELLED,
                "client_id": client1.id,
                "master_id": None,
            },
            {
                "title": "Ремонт стиральной машины (ОТМЕНЕНО)",
                "description": "Заявка отменена - оказалось, что проблема была в розетке, а не в машине.",
                "price": 1500.0,
                "address": "ул. Зелёная, 77, кв. 2",
                "category": "Бытовая техника",
                "status": TicketStatus.CANCELLED,
                "client_id": client2.id,
                "master_id": None,
            },
        ]
        
        for ticket_data in tickets_data:
            ticket = Ticket(**ticket_data)
            session.add(ticket)
        
        await session.flush()
        
        print(f"\n✅ Создано заявок: {len(tickets_data)}")
        print(f"   - {len([t for t in tickets_data if t['status'] == TicketStatus.NEW])} со статусом NEW")
        print(f"   - {len([t for t in tickets_data if t['status'] == TicketStatus.IN_PROGRESS])} со статусом IN_PROGRESS")
        print(f"   - {len([t for t in tickets_data if t['status'] == TicketStatus.DONE])} со статусом DONE")
        print(f"   - {len([t for t in tickets_data if t['status'] == TicketStatus.CANCELLED])} со статусом CANCELLED")
        
        # Сохраняем всё
        await session.commit()
        print("\n✅ Начальные данные успешно загружены!")


async def main():
    """Главная функция."""
    print("🌱 Начинаем заполнение БД начальными данными...\n")
    await seed_database()


if __name__ == "__main__":
    asyncio.run(main())
