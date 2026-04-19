#!/bin/bash

# Скрипт для запуска тестов
# Использование: bash scripts/test.sh

set -e

echo "🧪 Запуск тестов..."
echo ""

# Фаззинг-тесты с hypothesis
echo "Running fuzz tests with hypothesis..."
docker-compose exec -T backend pytest tests/test_fuzz.py -v

echo ""
echo "✅ Все тесты пройдены!"
