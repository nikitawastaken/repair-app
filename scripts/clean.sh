#!/bin/bash

# Скрипт для очистки проекта
# Использование: bash scripts/clean.sh

set -e

echo "🧹 Очистка проекта..."
echo ""

echo "Stopping Docker containers..."
docker-compose down

echo "Removing volumes..."
docker-compose down -v

echo ""
echo "✅ Проект очищен!"
echo "Для переинициализации запустите: bash scripts/init.sh"
