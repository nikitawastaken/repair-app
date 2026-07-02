#!/bin/bash

# Скрипт для инициализации production конфигурации
# Использование: bash scripts/prod/init.sh

set -e

echo "🚀 Инициализация Repair App (prod)..."

echo ""
if [ ! -f .env.prod ]; then
    echo "📝 Копирование .env.prod.example в .env.prod..."
    cp .env.prod.example .env.prod
    echo "✅ .env.prod создан"
fi

echo ""
echo "�️ Проверка production конфигурации..."
python3 - <<'PY'
import secrets
from pathlib import Path

path = Path('.env.prod')
lines = path.read_text().splitlines()
out = []
secret_set = False
app_env_set = False
for line in lines:
    if line.startswith('APP_ENV='):
        out.append('APP_ENV=production')
        app_env_set = True
    elif line.startswith('SECRET_KEY='):
        key = line.split('=', 1)[1].strip()
        if key in ('', 'your-secret-key-here', 'your-secret-key-here-change-in-production', 'dev-secret-key'):
            key = secrets.token_hex(32)
            out.append(f'SECRET_KEY={key}')
        else:
            out.append(line)
        secret_set = True
    else:
        out.append(line)
if not app_env_set:
    out.append('APP_ENV=production')
if not secret_set:
    out.append(f'SECRET_KEY={secrets.token_hex(32)}')
path.write_text('\n'.join(out) + '\n')
print('✅ .env.prod обновлен для production')
PY

echo ""
echo "�🐳 Запуск Docker Compose prod..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

echo ""
echo "⏳ Ожидание подготовки БД..."
sleep 5

echo ""
echo "🔄 Применение миграций..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod exec -T backend alembic upgrade head

echo ""
echo "🌱 Заполнение тестовыми данными..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod exec -T backend python -m app.seed

echo ""
echo "✅ Production инициализация завершена!"

echo ""
echo "🌐 Откройте в браузере:"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000"
