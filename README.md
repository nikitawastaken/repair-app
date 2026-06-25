# Repair App — Открытая площадка для заявок на ремонт

Приложение-площадка, где клиенты публикуют заявки на ремонт, мастера самостоятельно берут работу, а администраторы выступают модераторами.

## Описание

**Repair App** — это двусторонняя площадка услуг по ремонту:

- **Клиенты** создают заявки с описанием проблемы, указывают цену и адрес, а затем смотрят как мастера берут их работу
- **Мастера** видят доску открытых заявок, могут взять любую в работу, отказаться или завершить задачу
- **Администраторы** модерируют всю платформу: удаляют неуместные заявки и блокируют нарушителей

## Ключевые особенности

✅ **Открытая доска заявок** — мастера видят все открытые заявки и выбирают сами  
✅ **Фильтрация и поиск** — по категории, цене, названию  
✅ **Полная история** — клиенты видят статус заявки в реальном времени  
✅ **RBAC** — три типа ролей с разными правами доступа  
✅ **Модерация** — админ может удалить заявку и заблокировать пользователя  

## Быстрый старт

```bash
cd repair-app
docker-compose up -d --build
sleep 10
docker-compose exec backend alembic upgrade head
docker-compose exec backend python -m app.seed
```

## Доступ

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: postgres://user:password@localhost:5432/repair_app

## Тестовые аккаунты

| Email | Пароль | Роль | Описание |
|-------|--------|------|---------|
| admin@repair.ru | Admin1234! | Администратор | Модератор площадки |
| master1@repair.ru | Master123! | Мастер | Исполнитель услуг |
| master2@repair.ru | Master123! | Мастер | Исполнитель услуг |
| client1@repair.ru | Client123! | Клиент | Заказчик услуг |
| client2@repair.ru | Client123! | Клиент | Заказчик услуг |

## Модель данных

### User (Пользователь)

```
id: int (PK)
email: str (уникален)
hashed_password: str
full_name: str
role: enum("admin", "master", "client")
is_blocked: bool (блокировка администратором)
created_at: datetime
```

### Ticket (Заявка)

```
id: int (PK)
title: str (название проблемы)
description: str (полное описание)
price: float (предлагаемая сумма)
address: str (адрес выполнения работ)
category: str (категория: Сантехника, Электрика, Мебель и т.д.)
status: enum("new", "in_progress", "done", "cancelled")
client_id: int (FK → User, создатель)
master_id: int | null (FK → User, исполнитель)
created_at: datetime
updated_at: datetime
```

## Переходы статусов

```
new (новая)
  ↓ мастер берёт заявку → in_progress
  ↓ клиент отзывает → cancelled

in_progress (в работе)
  ↓ мастер завершает → done
  ↓ мастер отказывается → new

done (завершена)
  ✓ финальный статус

cancelled (отменена)
  ✓ финальный статус
```

## API Endpoints

### Аутентификация — `/auth`

| Метод | Путь | Доступ | Описание |
|-------|------|--------|---------|
| POST | `/auth/register` | Публичный | Регистрация (роль: client или master) |
| POST | `/auth/login` | Публичный | Логин, возвращает JWT token |
| GET | `/auth/me` | Авторизованный | Информация о текущем пользователе |

### Заявки — `/tickets`

| Метод | Путь | Доступ | Описание |
|-------|------|--------|---------|
| GET | `/tickets` | Авторизованный | Список заявок (с фильтрацией) |
| POST | `/tickets` | Клиент | Создать новую заявку |
| GET | `/tickets/{id}` | Авторизованный | Получить деталь заявки |
| PATCH | `/tickets/{id}/take` | Мастер | Взять заявку в работу (new → in_progress) |
| PATCH | `/tickets/{id}/done` | Мастер | Завершить заявку (in_progress → done) |
| PATCH | `/tickets/{id}/abandon` | Мастер | Отказаться от заявки (in_progress → new) |
| PATCH | `/tickets/{id}/cancel` | Клиент | Отозвать заявку (new → cancelled) |

### Администратор — `/admin`

| Метод | Путь | Доступ | Описание |
|-------|------|--------|---------|
| GET | `/admin/tickets` | Администратор | Все заявки (все статусы) |
| DELETE | `/admin/tickets/{id}` | Администратор | Удалить заявку |
| GET | `/admin/users` | Администратор | Список всех пользователей |
| PATCH | `/admin/users/{id}/block` | Администратор | Заблокировать/разблокировать пользователя |

## Фильтрация и поиск заявок

GET `/tickets` поддерживает следующие query-параметры:

| Параметр | Тип | Описание | Пример |
|----------|-----|---------|--------|
| `status` | string | Статус заявки | `status=new` |
| `category` | string | Категория | `category=Электрика` |
| `search` | string | Поиск по названию/описанию | `search=холодильник` |
| `min_price` | float | Минимальная цена | `min_price=500` |
| `max_price` | float | Максимальная цена | `max_price=5000` |
| `sort_by` | string | Сортировка (created_at или price) | `sort_by=price` |
| `order` | string | Порядок (asc или desc) | `order=asc` |

**Примеры:**
```bash
# Получить открытые заявки по электрике до 3000 рублей
GET /tickets?status=new&category=Электрика&max_price=3000

# Найти заявки по названию "холодильник", отсортировать по цене
GET /tickets?search=холодильник&sort_by=price&order=desc

# Для мастера: по умолчанию показываются только new заявки
GET /tickets  # Вернёт только new
```

## Роли и права доступа

### Клиент
- ✅ Регистрация и логин
- ✅ Создание заявок (с полями: title, description, price, address, category)
- ✅ Просмотр своих заявок
- ✅ Отзыв заявки (статус new → cancelled)
- ❌ Просмотр чужих заявок
- ❌ Взятие заявок в работу

### Мастер
- ✅ Регистрация и логин
- ✅ Просмотр всех открытых заявок (status = new) с фильтрацией
- ✅ Взятие заявки в работу (new → in_progress)
- ✅ Завершение заявки (in_progress → done)
- ✅ Отказ от заявки (in_progress → new, master_id = null)
- ✅ Просмотр своих активных и завершённых заявок
- ❌ Просмотр чужих заявок (кроме назначенных)
- ❌ Создание заявок

### Администратор
- ✅ Все операции клиента и мастера
- ✅ Просмотр всех заявок (все статусы)
- ✅ Удаление заявок
- ✅ Просмотр всех пользователей
- ✅ Блокировка/разблокировка пользователей
- ✅ Заблокированный пользователь не может логиниться

## Структура проекта

```
repair-app/
├── backend/                      # FastAPI сервер
│   ├── app/
│   │   ├── models/              # SQLModel модели (User, Ticket)
│   │   ├── services/            # Бизнес-логика
│   │   ├── routers/             # API эндпоинты (auth, tickets, admin)
│   │   ├── schemas/             # Pydantic схемы
│   │   ├── dependencies.py      # Зависимости (auth, rbac)
│   │   ├── config.py            # Настройки
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── main.py              # FastAPI app
│   │   └── seed.py              # Инициализация данных
│   ├── alembic/                 # Миграции БД
│   │   └── versions/            # Версии миграций
│   ├── tests/                   # Тесты
│   └── requirements.txt
├── frontend/                     # Vue 3 + Vite
│   ├── src/
│   │   ├── components/          # Компоненты (Board, MyTickets и т.д.)
│   │   ├── views/               # Страницы (ClientView, MasterBoardView и т.д.)
│   │   ├── stores/              # Pinia stores (auth, tickets)
│   │   ├── router/              # Vue Router с guard'ами
│   │   └── App.vue
│   └── package.json
├── scripts/                      # Утилиты (init.sh, test.sh и т.д.)
└── docker-compose.yml           # Orchestration
```

## Команды разработки

```bash
# Запуск всего
docker-compose up -d --build

# Логи бэкенда
docker-compose logs -f backend

# Логи фронтенда
docker-compose logs -f frontend

# Логи БД
docker-compose logs -f db

# Перезагрузка бэкенда
docker-compose restart backend

# Остановка и очистка
docker-compose down -v

# Применить миграции вручную
docker-compose exec backend alembic upgrade head

# Откатить миграции
docker-compose exec backend alembic downgrade -1

# Запустить seed
docker-compose exec backend python -m app.seed
```

## Технологический стек

### Backend
- **Python 3.11**
- **FastAPI 0.104** — асинхронный веб-фреймворк
- **SQLModel 0.0.14** — ORM (комбинирует SQLAlchemy + Pydantic)
- **SQLAlchemy 2.0** — работа с БД
- **Alembic 1.12** — миграции БД
- **asyncpg** — асинхронный драйвер PostgreSQL
- **python-jose** — JWT токены
- **passlib + bcrypt** — хеширование паролей
- **pydantic-settings** — управление конфигурацией

### Frontend
- **Vue 3** (Composition API)
- **Vite** — сборщик
- **Vue Router** — маршрутизация с RBAC гардами
- **Pinia** — управление состоянием
- **Axios** — HTTP клиент

### Database
- **PostgreSQL 15** — реляционная БД
- **Timezone-aware timestamps** — все даты с UTC

### DevOps
- **Docker** — контейнеризация
- **Docker Compose** — оркестрация контейнеров

## Особенности реализации

1. **Timezone-aware datetimes**: Все timestamp'ы хранятся в UTC с указанием часового пояса
2. **Идемпотентный seed**: Запуск `seed.py` несколько раз не создаёт дубликаты
3. **RBAC в зависимостях**: `get_current_user`, `get_current_admin`, `get_current_master`, `get_current_client`
4. **Миграции БД**: Используется Alembic для версионирования схемы
6. **Blocking users**: Заблокированные пользователи не могут логиниться (HTTP 403)

## Развёртывание в облаке

Для production:

1. Изменить `docker-compose.prod.yml`:
   - Использовать управляемый PostgreSQL (AWS RDS, Google Cloud SQL и т.д.)
   - Настроить CORS на основной домен
   - Использовать HTTPS

2. Secrets:
   - `SECRET_KEY` — в AWS Secrets Manager или аналог
   - `DATABASE_URL` — в переменных окружения
   - `CORS_ORIGINS` — ограничить до одного домена

3. CI/CD:
   - GitHub Actions / GitLab CI для запуска тестов
   - Развёртывание на Heroku, AWS, Google Cloud и т.д.

## Поддержка и вклад

Для багов и идей — создавайте Issues. 

Лицензия: MIT
