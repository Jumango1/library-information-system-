# 📚 Библиотечная информационная система

> **Магистерская работа** по дисциплине "Архитектура предприятий и информационных систем"  
> **Вариант 6** - Комплексная система управления библиотекой

## 🎯 Описание проекта

Enterprise-уровень информационная система для управления библиотекой с полным циклом работы: каталог книг, читатели, выдачи, аналитика и отчетность.

### ✨ Ключевые возможности

- ✅ **16 SQL запросов** из методички (вариант 6)
- ✅ **REST API** с полной документацией
- ✅ **Веб-интерфейс** с Bootstrap 5
- ✅ **Экспорт данных** в Excel и PDF
- ✅ **Docker-контейнеризация** всех сервисов
- ✅ **PostgreSQL** база данных
- ✅ **Nginx** reverse proxy
- ✅ **pgAdmin** для администрирования БД
- ✅ **100+ записей** тестовых данных

## 🏗️ Архитектура системы

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (Port 80)                      │
│                   Reverse Proxy                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Flask Application (Port 5000)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   REST API   │  │  Web UI      │  │   Export     │  │
│  │   Endpoints  │  │  (Jinja2)    │  │  (PDF/Excel) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                   SQLAlchemy ORM                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           PostgreSQL 15 (Port 5432)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │  Books   │ │ Authors  │ │ Readers  │ │  Loans   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              pgAdmin 4 (Port 5050)                      │
│            Database Administration                      │
└─────────────────────────────────────────────────────────┘
```

## 🗄️ Модель данных

### Основные сущности

1. **Publishers** (Издательства)
   - id, name, city, country

2. **Authors** (Авторы)
   - id, first_name, last_name, birth_year, country

3. **Books** (Книги)
   - id, title, isbn, publication_year, pages
   - copies_total, copies_available, publisher_id, genre

4. **BookAuthors** (Связь книг и авторов)
   - Many-to-Many relationship

5. **Readers** (Читатели)
   - id, first_name, last_name, email, phone
   - address, registration_date

6. **Loans** (Выдачи)
   - id, book_id, reader_id
   - loan_date, due_date, return_date, status

## 🚀 Быстрый старт

### Предварительные требования

- Docker Desktop
- Git
- 4GB свободной RAM

### Установка и запуск

```bash
# 1. Клонировать репозиторий
git clone <repository-url>
cd library-information-system

# 2. Создать .env файл
cp .env.example .env

# 3. Запустить все сервисы
docker-compose up -d

# 4. Дождаться инициализации (30-60 секунд)
docker-compose logs -f app

# 5. Открыть в браузере
# Веб-интерфейс: http://localhost
# pgAdmin: http://localhost:5050
```

### Проверка работоспособности

```bash
# Проверить статус контейнеров
docker-compose ps

# Должны быть запущены:
# - library_db (PostgreSQL)
# - library_app (Flask)
# - library_nginx (Nginx)
# - library_pgadmin (pgAdmin)
```

## 📋 16 SQL запросов (Вариант 6)

| № | Описание | Endpoint | Параметры |
|---|----------|----------|-----------|
| 1 | Книги определенного автора | `/api/query1` | `?author=Толстой` |
| 2 | Книги определенного жанра | `/api/query2` | `?genre=Роман` |
| 3 | Доступные книги для выдачи | `/api/query3` | - |
| 4 | Активные выдачи книг | `/api/query4` | - |
| 5 | Просроченные выдачи | `/api/query5` | - |
| 6 | История выдач читателя | `/api/query6` | `?reader_id=1` |
| 7 | Самые популярные книги | `/api/query7` | - |
| 8 | Книги определенного издательства | `/api/query8` | `?publisher=Эксмо` |
| 9 | Книги изданные в году | `/api/query9` | `?year=2020` |
| 10 | Читатели с активными выдачами | `/api/query10` | - |
| 11 | Авторы из определенной страны | `/api/query11` | `?country=Россия` |
| 12 | Книги по количеству страниц | `/api/query12` | `?min=100&max=500` |
| 13 | Новые читатели за месяц | `/api/query13` | - |
| 14 | Книги никогда не выдававшиеся | `/api/query14` | - |
| 15 | Статистика по издательствам | `/api/query15` | - |
| 16 | Общая статистика выдач | `/api/query16` | - |

## 📊 Экспорт данных

Любой запрос можно экспортировать:

```bash
# Excel
curl "http://localhost/api/export/excel/query1?author=Толстой" -o report.xlsx

# PDF
curl "http://localhost/api/export/pdf/query7" -o popular_books.pdf
```

## 🔧 Администрирование

### pgAdmin

1. Открыть http://localhost:5050
2. Войти:
   - Email: `admin@library.com`
   - Password: `admin`
3. Добавить сервер:
   - Host: `db`
   - Port: `5432`
   - Database: `library_db`
   - Username: `library_user`
   - Password: `library_pass`

### Прямое подключение к БД

```bash
# Через Docker
docker exec -it library_db psql -U library_user -d library_db

# Локально (если установлен psql)
psql -h localhost -U library_user -d library_db
```

## 🛠️ Разработка

### Структура проекта

```
library-information-system/
├── app/
│   ├── app.py              # Главное Flask приложение
│   ├── models.py           # SQLAlchemy модели
│   ├── config.py           # Конфигурация
│   ├── requirements.txt    # Python зависимости
│   ├── Dockerfile          # Docker образ приложения
│   └── templates/
│       └── index.html      # Веб-интерфейс
├── db/
│   └── init.sql            # Seed данные
├── nginx/
│   └── nginx.conf          # Конфигурация Nginx
├── docker-compose.yml      # Оркестрация контейнеров
├── .env.example            # Пример переменных окружения
└── README.md               # Документация
```

### Локальная разработка

```bash
# Установить зависимости
cd app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Запустить Flask в dev режиме
export DATABASE_URL="postgresql://library_user:library_pass@localhost:5432/library_db"
flask run --debug
```

### Добавление новых запросов

1. Добавить endpoint в `app/app.py`:
```python
@app.route('/api/query17')
def query17_custom():
    # Ваш SQL запрос
    results = db.session.query(...).all()
    return jsonify([...])
```

2. Добавить карточку в `templates/index.html`

3. Перезапустить контейнер:
```bash
docker-compose restart app
```

## 🌐 Публичный доступ (для демонстрации)

### Вариант 1: ngrok (рекомендуется)

```bash
# Установить ngrok
# https://ngrok.com/download

# Запустить туннель
ngrok http 80

# Получите публичный URL типа:
# https://abc123.ngrok.io
```

### Вариант 2: Cloudflare Tunnel

```bash
# Установить cloudflared
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/

# Запустить туннель
cloudflared tunnel --url http://localhost:80
```

## 📈 Тестовые данные

Система поставляется с готовыми данными:

- **30 книг** (русская и зарубежная литература, IT-книги)
- **15 авторов** (Толстой, Достоевский, Orwell, Hemingway и др.)
- **8 издательств** (Эксмо, АСТ, Penguin, O'Reilly и др.)
- **16 читателей** из разных городов
- **24 выдачи** (активные, просроченные, возвращенные)

## 🎓 Для преподавателя

### Демонстрация возможностей

1. **Архитектура**: Микросервисная архитектура с контейнеризацией
2. **Масштабируемость**: Легко добавить реплики через docker-compose
3. **Безопасность**: Nginx как reverse proxy, изоляция сервисов
4. **Мониторинг**: pgAdmin для контроля БД
5. **API-first**: REST API с возможностью интеграции
6. **Отчетность**: Экспорт в стандартные форматы

### Технологический стек

- **Backend**: Python 3.11, Flask 3.0
- **ORM**: SQLAlchemy 3.1
- **Database**: PostgreSQL 15
- **Frontend**: Bootstrap 5, Vanilla JS
- **Proxy**: Nginx Alpine
- **Containerization**: Docker, Docker Compose
- **Export**: ReportLab (PDF), OpenPyXL (Excel)

## 🔍 Troubleshooting

### Порты заняты

```bash
# Изменить порты в docker-compose.yml
ports:
  - "8080:80"    # Nginx
  - "5001:5000"  # Flask
  - "5433:5432"  # PostgreSQL
  - "5051:80"    # pgAdmin
```

### База данных не инициализируется

```bash
# Пересоздать контейнеры
docker-compose down -v
docker-compose up -d
```

### Ошибки импорта Python

```bash
# Пересобрать образ
docker-compose build --no-cache app
docker-compose up -d
```

## 📝 Лицензия

Учебный проект для магистерской программы.

## 👨‍💻 Автор

Магистрант, Архитектура предприятий и информационных систем

---

**Дата создания**: Май 2026  
**Версия**: 1.0.0  
**Статус**: Production Ready ✅
