#!/bin/bash

# Скрипт для перезагрузки проекта
# Использование: bash scripts/restart.sh

set -e

echo "🔄 Перезагрузка Repair App..."
echo ""

# Останавливаем контейнеры
echo "Stopping containers..."
docker-compose stop

# Запускаем снова
echo "Starting containers..."
docker-compose start

echo ""
echo "✅ Перезагрузка завершена!"
echo ""
echo "Проверьте логи: bash scripts/logs.sh"
