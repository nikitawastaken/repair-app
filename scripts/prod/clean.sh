#!/bin/bash

# Скрипт для очистки production конфигурации
# Использование: bash scripts/prod/cleanup.sh

set -e

echo "🧹 Очистка production окружения..."

docker-compose -f docker-compose.prod.yml --env-file .env.prod down -v

echo ""
echo "✅ Production окружение очищено!"
