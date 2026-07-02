#!/bin/bash

# Скрипт для запуска тестов
# Использование: bash scripts/test.sh

set -e

echo "🧪 Запуск тестов..."
echo ""

echo "Running fuzzing tests with hypothesis..."
docker-compose exec -T -e TESTING=1 backend pytest tests/test_fuzz.py -v

echo ""
echo "✅ Все тесты пройдены!"
