#!/bin/bash

echo "🚀 Запуск библиотечной информационной системы..."
echo ""

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Проверка Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен."
    exit 1
fi

echo "✅ Docker установлен"

# Создание .env если не существует
if [ ! -f .env ]; then
    echo "📝 Создание .env файла..."
    cp .env.example .env
    echo "✅ .env создан"
fi

# Остановка старых контейнеров
echo "🛑 Остановка старых контейнеров..."
docker-compose down 2>/dev/null

# Запуск контейнеров
echo "🐳 Запуск Docker контейнеров..."
docker-compose up -d

# Ожидание запуска
echo "⏳ Ожидание инициализации (30 секунд)..."
sleep 30

# Проверка статуса
echo ""
echo "📊 Статус контейнеров:"
docker-compose ps

echo ""
echo "✅ Система запущена!"
echo ""
echo "🌐 Доступные сервисы:"
echo "   • Веб-интерфейс: http://localhost"
echo "   • pgAdmin:       http://localhost:5050"
echo ""
echo "📚 Документация:"
echo "   • README.md      - Полная документация"
echo "   • QUICKSTART.md  - Быстрый старт"
echo "   • docs/ARCHITECTURE.md - Архитектура"
echo ""
echo "🔍 Полезные команды:"
echo "   docker-compose logs -f app    # Логи приложения"
echo "   docker-compose down           # Остановить систему"
echo "   docker-compose restart        # Перезапустить"
echo ""
