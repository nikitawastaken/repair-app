#!/bin/bash

# Скрипт для инициализации проекта
# Использование: bash scripts/init.sh

set -e

echo "🚀 Инициализация Repair App..."
echo ""

# 1. Создаём .env файл если его нет
if [ ! -f .env ]; then
    echo "📝 Копирование .env.example в .env..."
    cp .env.example .env
    echo "✅ .env создан"
fi

# 2. Запускаем Docker Compose
echo ""
echo "🐳 Запуск Docker Compose..."
docker-compose up -d --build

# 3. Ждём, чтобы БД была готова
echo ""
echo "⏳ Ожидание подготовки БД..."
sleep 5

# 4. Применяем миграции
echo ""
echo "🔄 Применение миграций..."
docker-compose exec -T backend alembic upgrade head

# 5. Заполняем тестовыми данными
echo ""
echo "🌱 Заполнение тестовыми данными..."
docker-compose exec -T backend python -m app.seed

echo ""
echo "✅ Инициализация завершена!"
echo ""
echo "🌐 Откройте в браузере:"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000"
echo "   Swagger:   http://localhost:8000/docs"
