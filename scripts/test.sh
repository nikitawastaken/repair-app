#!/bin/bash

# Скрипт для запуска тестов
# Использование: bash scripts/test.sh

set -e

echo "🧪 Запуск тестов..."
echo ""

echo "Running backend tests..."
docker-compose exec -T backend pytest -q

echo ""
echo "✅ Все тесты пройдены!"
