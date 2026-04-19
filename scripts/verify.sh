#!/bin/bash

# Скрипт для проверки требований и установки
# Использование: bash scripts/verify.sh

set -e

echo "🔍 Проверка требований для Repair App..."
echo ""

# Проверяем Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker установлен: $(docker --version)"
else
    echo "❌ Docker не найден. Установите: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Проверяем Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose установлен: $(docker-compose --version)"
else
    echo "❌ Docker Compose не найден. Установите: https://docs.docker.com/compose/install/"
    exit 1
fi

# Проверяем Git
if command -v git &> /dev/null; then
    echo "✅ Git установлен: $(git --version)"
else
    echo "❌ Git не найден. Установите: https://git-scm.com/"
    exit 1
fi

# Проверяем, что Docker работает
if docker ps &> /dev/null; then
    echo "✅ Docker daemon работает"
else
    echo "❌ Docker daemon не запущен. Запустите Docker Desktop"
    exit 1
fi

# Проверяем, что порты свободны
echo ""
echo "🔍 Проверка портов..."

if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️ Порт 5173 (frontend) занят"
else
    echo "✅ Порт 5173 свободен"
fi

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️ Порт 8000 (backend) занят"
else
    echo "✅ Порт 8000 свободен"
fi

if lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️ Порт 5432 (БД) занят"
else
    echo "✅ Порт 5432 свободен"
fi

echo ""
echo "✅ Все требования выполнены!"
echo ""
echo "Для начала работы выполните:"
echo "  bash scripts/init.sh"
echo ""
