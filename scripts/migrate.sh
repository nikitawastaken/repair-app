#!/bin/bash

# Скрипт для миграций БД
# Использование: bash scripts/migrate.sh [upgrade|downgrade|current]

set -e

COMMAND=${1:-upgrade}
REVISION=${2:-head}

echo "🔄 Выполнение миграции: $COMMAND $REVISION..."
echo ""

docker-compose exec -T backend alembic $COMMAND $REVISION

echo ""
echo "✅ Миграция завершена!"
