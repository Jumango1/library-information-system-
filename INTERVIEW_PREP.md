# Ответы на возможные вопросы

## 1. Технические вопросы о SQL запросах

### "Покажите самый сложный запрос и объясните как он работает"

**Query 7 - Популярные книги:**
```python
popular = db.session.query(
    Book.title,
    func.count(Loan.id).label('loan_count')
).join(Loan).group_by(Book.id, Book.title).order_by(func.count(Loan.id).desc()).limit(10).all()
```

**Объяснение:**
- JOIN между Book и Loan - связываем книги с выдачами
- GROUP BY по Book.id - группируем по книгам
- COUNT(Loan.id) - считаем количество выдач для каждой книги
- ORDER BY DESC - сортируем от большего к меньшему
- LIMIT 10 - берём топ-10

**Почему медленно на больших данных:**
- Нет индекса на book_id в таблице loans
- Полное сканирование таблицы при JOIN
- Решение: добавить индекс `CREATE INDEX idx_loans_book_id ON loans(book_id)`

### "Как защищены от SQL injection?"

**Используется ORM (SQLAlchemy):**
```python
# Плохо (уязвимо):
query = f"SELECT * FROM books WHERE title = '{user_input}'"

# Хорошо (безопасно):
Book.query.filter(Book.title == user_input).all()
```

SQLAlchemy автоматически экранирует параметры и использует prepared statements.

### "Почему используете ilike вместо like?"

```python
Author.last_name.ilike(f'%{author_name}%')
```

- `ilike` - case-insensitive поиск (не зависит от регистра)
- Работает в PostgreSQL
- Пользователь может ввести "толстой" или "Толстой" - найдёт в обоих случаях

---

## 2. Архитектурные вопросы

### "Почему выбрали микросервисную архитектуру?"

**Преимущества:**
1. **Изоляция** - падение одного сервиса не роняет всю систему
2. **Масштабируемость** - можем добавить реплики Flask без пересборки БД
3. **Независимое развёртывание** - обновляем app без остановки БД
4. **Технологическая гибкость** - можем заменить Flask на FastAPI без изменения БД

**Недостатки:**
- Сложнее в разработке
- Больше overhead на сетевые запросы
- Нужен Docker

**Почему это оправдано:**
- Система предполагает рост
- Нужна высокая доступность
- Разные команды могут работать над разными сервисами

### "Почему Flask, а не Django?"

**Flask:**
- Легковесный - быстрее стартует
- Гибкий - выбираем только нужные компоненты
- Простой для API - не нужен весь Django ORM и admin
- Меньше overhead

**Django:**
- Тяжелее
- Много встроенного, что не нужно (admin, forms, auth)
- Больше conventions - меньше гибкости

**Для этого проекта Flask лучше:**
- Нужен только REST API + простой UI
- Не нужна админка Django
- Хотим контроль над архитектурой

### "Почему PostgreSQL, а не MySQL или MongoDB?"

**PostgreSQL:**
- Лучшая поддержка JSON (если понадобится)
- ACID транзакции
- Мощные индексы (GiST, GIN)
- Лучше для сложных запросов с JOIN

**MySQL:**
- Проще, но слабее в сложных запросах
- Хуже поддержка JSON

**MongoDB:**
- NoSQL - не подходит для реляционных данных
- У нас чёткие связи: книги-авторы, книги-выдачи
- Нужны JOIN'ы и транзакции

### "Зачем Nginx, если Flask может сам отдавать статику?"

**Nginx как reverse proxy:**
1. **Производительность** - Nginx быстрее отдаёт статику
2. **Load balancing** - можем добавить несколько Flask инстансов
3. **SSL termination** - Nginx обрабатывает HTTPS
4. **Кеширование** - Nginx кеширует ответы
5. **Безопасность** - скрывает внутреннюю архитектуру

**Production best practice:**
- Flask для бизнес-логики
- Nginx для статики и проксирования

---

## 3. Безопасность

### "Какие меры безопасности реализованы?"

**1. SQL Injection защита:**
- Используем ORM (SQLAlchemy)
- Все параметры экранируются автоматически

**2. Изоляция контейнеров:**
- Каждый сервис в отдельном контейнере
- Docker networks - сервисы не видят друг друга напрямую

**3. Секреты в переменных окружения:**
- Пароли БД в .env файле
- .env в .gitignore - не попадает в Git

**4. Nginx как reverse proxy:**
- Скрывает внутреннюю архитектуру
- Flask не доступен напрямую извне

**Что нужно добавить для production:**
- HTTPS с SSL сертификатами
- Rate limiting (защита от DDoS)
- JWT аутентификация
- CORS настройки
- Input validation на уровне API

### "Как защищены от XSS?"

**Jinja2 автоматически экранирует:**
```html
{{ book.title }}  <!-- Автоматически экранируется -->
```

Если в title будет `<script>alert('xss')</script>`, Jinja2 превратит в:
```html
&lt;script&gt;alert('xss')&lt;/script&gt;
```

**Для JSON API:**
- Flask jsonify() автоматически экранирует
- Content-Type: application/json - браузер не выполняет как HTML

---

## 4. Масштабируемость

### "Как система будет работать при росте нагрузки?"

**Горизонтальное масштабирование:**

```yaml
# docker-compose.yml
services:
  app:
    deploy:
      replicas: 5  # 5 инстансов Flask
    
  nginx:
    # Load balancing между репликами
```

**Вертикальное масштабирование:**
```yaml
services:
  db:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
```

**Оптимизации:**
1. **Connection pooling** - SQLAlchemy pool (уже есть)
2. **Индексы БД** - на часто запрашиваемых полях
3. **Кеширование** - Redis для популярных запросов
4. **CDN** - для статики (Bootstrap, Font Awesome)
5. **Database replication** - read replicas для чтения

**Узкие места:**
- Query 7 (популярные книги) - медленный без индекса
- Экспорт в PDF - синхронный, блокирует
- Нет кеширования

**Решения:**
- Добавить индексы
- Вынести экспорт в Celery (асинхронно)
- Добавить Redis для кеша

### "Сколько пользователей выдержит?"

**Текущая конфигурация:**
- 1 Flask инстанс: ~100 req/sec
- PostgreSQL: ~1000 req/sec
- Nginx: ~10000 req/sec

**Узкое место:** Flask

**С масштабированием (5 реплик Flask):**
- ~500 req/sec
- ~43 миллиона запросов в день
- ~1000-5000 одновременных пользователей

**Для больших нагрузок:**
- Kubernetes вместо Docker Compose
- Database sharding
- Microservices (разделить на book-service, loan-service)

---

## 5. Разработка и развёртывание

### "Как развёртывается в production?"

**Текущий способ (dev):**
```bash
docker-compose up -d
```

**Production способ:**
1. **CI/CD pipeline:**
   - GitHub Actions
   - Тесты → Build → Deploy

2. **Kubernetes:**
   - Helm charts
   - Auto-scaling
   - Rolling updates

3. **Мониторинг:**
   - Prometheus + Grafana
   - Логи в ELK stack
   - Alerting

### "Как тестируете?"

**Что нужно добавить:**
```python
# tests/test_api.py
def test_query1_books_by_author():
    response = client.get('/api/query1?author=Толстой')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0
    assert 'Война и мир' in [b['title'] for b in data]
```

**Типы тестов:**
- Unit tests - тестируем функции
- Integration tests - тестируем API endpoints
- E2E tests - тестируем через браузер (Selenium)

### "Как мигрируете базу данных?"

**Flask-Migrate (Alembic):**
```bash
# Создать миграцию
flask db migrate -m "Add index to loans"

# Применить миграцию
flask db upgrade

# Откатить
flask db downgrade
```

**Текущая проблема:**
- Используем init.sql вместо миграций
- Нет версионирования схемы

**Решение:**
- Перейти на Flask-Migrate
- Каждое изменение схемы = новая миграция

---

## 6. Бизнес-логика

### "Что происходит при выдаче книги?"

**Должно быть (но не реализовано):**
```python
@app.route('/api/loan/create', methods=['POST'])
def create_loan():
    book_id = request.json['book_id']
    reader_id = request.json['reader_id']
    
    # Проверяем доступность
    book = Book.query.get(book_id)
    if book.copies_available <= 0:
        return jsonify({'error': 'Книга недоступна'}), 400
    
    # Создаём выдачу
    loan = Loan(
        book_id=book_id,
        reader_id=reader_id,
        loan_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=30),
        status='active'
    )
    
    # Уменьшаем количество доступных
    book.copies_available -= 1
    
    db.session.add(loan)
    db.session.commit()
    
    return jsonify({'success': True})
```

**Проблемы:**
- Нет транзакций (race condition)
- Нет проверки на дубликаты
- Нет уведомлений

### "Как обрабатываете просроченные книги?"

**Текущая реализация:**
- Query 5 показывает просроченные
- Но нет автоматических действий

**Что нужно добавить:**
```python
# Cron job или Celery task
@celery.task
def check_overdue_loans():
    overdue = Loan.query.filter(
        Loan.status == 'active',
        Loan.due_date < datetime.utcnow()
    ).all()
    
    for loan in overdue:
        # Отправить email читателю
        send_email(loan.reader.email, 'Просрочена книга')
        
        # Обновить статус
        loan.status = 'overdue'
    
    db.session.commit()
```

---

## Краткие ответы на быстрые вопросы

**"Сколько времени разрабатывали?"**
- "Около недели на базовую версию, потом итеративно улучшал"

**"Почему не использовали готовое решение?"**
- "Хотел понять архитектуру с нуля, готовые решения - чёрный ящик"

**"Планируете развивать проект?"**
- "Да, хочу добавить мобильное приложение и улучшить аналитику"

**"Какие были сложности?"**
- "Настройка Docker networking, оптимизация сложных JOIN запросов"

**"Что бы сделали по-другому?"**
- "Добавил бы тесты с самого начала, использовал бы миграции вместо init.sql"
