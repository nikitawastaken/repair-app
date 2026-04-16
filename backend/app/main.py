"""
Главный файл приложения FastAPI.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import auth_router, tickets_router, admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация и очистка приложения."""
    # При запуске: инициализируем БД
    await init_db()
    yield
    # При остановке: очистка (если требуется)


app = FastAPI(
    title="Repair App API",
    description="API для приложения обработки заявок на ремонт",
    version="1.0.0",
    lifespan=lifespan,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth_router)
app.include_router(tickets_router)
app.include_router(admin_router)


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {
        "message": "Добро пожаловать в Repair App API",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения."""
    return {"status": "ok"}
