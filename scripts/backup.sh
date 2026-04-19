#!/bin/bash

# Скрипт для создания резервной копии БД
# Использование: bash scripts/backup.sh

set -e

echo "💾 Создание резервной копии БД..."
echo ""

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${TIMESTAMP}.sql"

docker-compose exec -T db pg_dump -U postgres repairdb > "$BACKUP_FILE"

echo "✅ Резервная копия создана: $BACKUP_FILE"
echo ""
echo "Для восстановления используйте:"
echo "  docker-compose exec -T db psql -U postgres repairdb < $BACKUP_FILE"
