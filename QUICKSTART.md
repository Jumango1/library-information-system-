# Быстрый старт

## Запуск системы за 3 команды

```bash
# 1. Создать .env файл
cp .env.example .env

# 2. Запустить все контейнеры
docker-compose up -d

# 3. Открыть браузер
# http://localhost
```

## Проверка работы

```bash
# Статус контейнеров
docker-compose ps

# Логи приложения
docker-compose logs -f app

# Проверка БД
docker exec -it library_db psql -U library_user -d library_db -c "\dt"
```

## Доступ к сервисам

- **Веб-интерфейс**: http://localhost
- **pgAdmin**: http://localhost:5050
  - Email: admin@library.com
  - Password: admin

## Остановка

```bash
# Остановить контейнеры
docker-compose down

# Удалить всё включая данные
docker-compose down -v
```

## Публичный доступ (для демонстрации преподавателю)

### Вариант 1: ngrok (рекомендуется)

```bash
# Скачать: https://ngrok.com/download
ngrok http 80

# Получите URL типа: https://abc123.ngrok.io
# Отправьте этот URL преподавателю
```

### Вариант 2: Показать с телефона

```bash
# Узнать IP компьютера
ipconfig  # Windows
ifconfig  # Linux/Mac

# Открыть на телефоне
# http://192.168.x.x
```

## Демонстрация возможностей

1. **Главная страница** - Статистика и дашборд
2. **16 запросов** - Все запросы из методички
3. **Экспорт** - PDF и Excel отчеты
4. **pgAdmin** - Администрирование БД
5. **API** - REST endpoints

## Troubleshooting

### Порт 80 занят

```bash
# Изменить в docker-compose.yml
ports:
  - "8080:80"  # Вместо 80:80

# Открыть: http://localhost:8080
```

### Контейнеры не запускаются

```bash
# Пересоздать всё
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### База данных пустая

```bash
# Проверить логи
docker-compose logs db

# Вручную загрузить данные
docker exec -i library_db psql -U library_user library_db < db/init.sql
```
