@echo off
echo 🚀 Запуск библиотечной информационной системы...
echo.

REM Проверка Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не установлен. Установите Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo ✅ Docker установлен

REM Создание .env если не существует
if not exist .env (
    echo 📝 Создание .env файла...
    copy .env.example .env
    echo ✅ .env создан
)

REM Остановка старых контейнеров
echo 🛑 Остановка старых контейнеров...
docker-compose down 2>nul

REM Запуск контейнеров
echo 🐳 Запуск Docker контейнеров...
docker-compose up -d

REM Ожидание запуска
echo ⏳ Ожидание инициализации (30 секунд)...
timeout /t 30 /nobreak >nul

REM Проверка статуса
echo.
echo 📊 Статус контейнеров:
docker-compose ps

echo.
echo ✅ Система запущена!
echo.
echo 🌐 Доступные сервисы:
echo    • Веб-интерфейс: http://localhost
echo    • pgAdmin:       http://localhost:5050
echo.
echo 📚 Документация:
echo    • README.md      - Полная документация
echo    • QUICKSTART.md  - Быстрый старт
echo    • docs/ARCHITECTURE.md - Архитектура
echo.
echo 🔍 Полезные команды:
echo    docker-compose logs -f app    # Логи приложения
echo    docker-compose down           # Остановить систему
echo    docker-compose restart        # Перезапустить
echo.
pause
