#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "Закрытие старых контейнеров"
docker-compose -f "${PROJECT_DIR}/docker-compose.yml" down

echo -e "Создание билдов для сайта"
docker-compose -f "${PROJECT_DIR}/docker-compose.yml" build

echo -e "Запуск сервисов с помощью Docker Compose..."
docker-compose -f "${PROJECT_DIR}/docker-compose.yml" up

echo -e "Сайт успешно запущен!"
