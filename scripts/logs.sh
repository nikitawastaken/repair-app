#!/bin/bash

# Скрипт для просмотра логов
# Использование: bash scripts/logs.sh [backend|frontend|db|all]

SERVICE=${1:-all}

case $SERVICE in
  backend)
    docker-compose logs -f backend
    ;;
  frontend)
    docker-compose logs -f frontend
    ;;
  db)
    docker-compose logs -f db
    ;;
  *)
    docker-compose logs -f
    ;;
esac
