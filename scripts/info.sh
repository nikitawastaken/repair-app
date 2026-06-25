#!/bin/bash

# Скрипт для проверки и вывода информации о проекте
# Использование: bash scripts/info.sh

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   Repair App — Приложение обработки заявок на ремонт           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo "📊 ИНФОРМАЦИЯ О ПРОЕКТЕ"
echo "=========================="
echo ""

# Версии
echo "🔧 Версии компонентов:"
echo "  - Python Backend: 3.11"
echo "  - FastAPI: 0.104.1"
echo "  - Vue Frontend: 3.3.8"
echo "  - PostgreSQL: 15"
echo "  - Node.js (Frontend): 20"
echo ""

# Файлы
echo "📁 Структура проекта:"
echo "  - Backend (Python): $(find backend -name '*.py' 2>/dev/null | wc -l) файлов"
echo "  - Frontend (Vue): $(find frontend -name '*.vue' -o -name '*.js' 2>/dev/null | wc -l) файлов"
echo "  - Скрипты: $(find scripts -name '*.sh' 2>/dev/null | wc -l) файлов"
echo "  - Документация: $(find . -maxdepth 1 -name '*.md' 2>/dev/null | wc -l) файлов"
echo ""

# Сервисы
echo "🐳 Docker сервисы:"
echo "  - PostgreSQL (порт 5432)"
echo "  - Backend API (порт 8000)"
echo "  - Frontend Web (порт 5173)"
echo ""

# API
echo "📡 API Эндпоинты:"
echo "  - Авторизация: 2 эндпоинта (register, login)"
echo "  - Заявки: 5 эндпоинтов (CRUD + assign)"
echo "  - Admin: 2 эндпоинта (users, roles)"
echo ""

# Тесты
echo "🧪 Тестирование:"
echo "  - Тесты: пока не реализованы"
echo "  - Покрытие: API stability (status < 500)"
echo ""

# Ролевая модель
echo "👥 Роли пользователей:"
echo "  - client: создание заявок, просмотр своих"
echo "  - master: просмотр назначенных, смена статусов"
echo "  - admin: управление всем"
echo ""

echo "🚀 БЫСТРЫЙ СТАРТ"
echo "=================================="
echo ""
echo "1️⃣  Проверить требования:"
echo "   bash scripts/verify.sh"
echo ""
echo "2️⃣  Инициализировать проект:"
echo "   bash scripts/init.sh"
echo ""
echo "3️⃣  Открыть в браузере:"
echo "   - Frontend: http://localhost:5173"
echo "   - Backend: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "4️⃣  Залогиниться с тестовым аккаунтом:"
echo "   Email: admin@repair.ru"
echo "   Password: Admin1234!"
echo ""

echo "📚 ДОКУМЕНТАЦИЯ"
echo "=================================="
echo "  - QUICKSTART.md  ← Быстрый старт"
echo "  - README.md      ← Описание проекта"
echo "  - SETUP.md       ← Детальная инструкция"
echo "  - API.md         ← API документация"
echo "  - TESTING.md     ← Тестирование"
echo "  - ARCHITECTURE.md ← Архитектура"
echo "  - INDEX.md       ← Полный индекс"
echo ""

echo "🛠️  ПОЛЕЗНЫЕ КОМАНДЫ"
echo "=================================="
echo "  - bash scripts/verify.sh    # Проверить требования"
echo "  - bash scripts/init.sh      # Инициализировать"
echo "  - bash scripts/test.sh      # Запустить тесты"
echo "  - bash scripts/logs.sh      # Просмотр логов"
echo "  - bash scripts/restart.sh   # Перезагрузить"
echo "  - bash scripts/clean.sh     # Полная очистка"
echo ""

echo "✅ Проект готов к использованию!"
echo ""
