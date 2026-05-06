from flask import Flask, render_template, jsonify, request, send_file
from flask_migrate import Migrate
from models import db, Book, Author, Reader, Loan, Publisher, BookAuthor
from config import Config
from datetime import datetime, timedelta
from sqlalchemy import text
import io
import os
import zipfile
import tempfile
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd

# TODO: вынести конфиг в отдельный файл, а то хуйня какая-то
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/books')
def get_books():
    # просто все книги, без всякой хуйни
    books = Book.query.all()
    return jsonify([{
        'id': b.id,
        'title': b.title,
        'isbn': b.isbn,
        'year': b.publication_year,
        'available': b.copies_available
    } for b in books])


@app.route('/api/readers')
def get_readers():
    readers = Reader.query.all()
    return jsonify([{
        'id': r.id,
        'name': f"{r.first_name} {r.last_name}",
        'email': r.email,
        'phone': r.phone
    } for r in readers])


@app.route('/api/loans')
def get_loans():
    loans = Loan.query.all()
    return jsonify([{
        'id': l.id,
        'book': l.book.title,
        'reader': f"{l.reader.first_name} {l.reader.last_name}",
        'loan_date': l.loan_date.strftime('%Y-%m-%d'),
        'due_date': l.due_date.strftime('%Y-%m-%d'),
        'status': l.status
    } for l in loans])


# Запросы - основная логика системы

@app.route('/api/query1')
def query1_books_by_author():
    """Все книги определенного автора"""
    author_name = request.args.get('author', 'Толстой')
    # join'ы работают, но можно было бы через relationship сделать
    books = db.session.query(Book).join(BookAuthor).join(Author).filter(
        (Author.last_name.ilike(f'%{author_name}%')) |
        (Author.first_name.ilike(f'%{author_name}%'))
    ).all()

    return jsonify([{
        'title': b.title,
        'year': b.publication_year,
        'isbn': b.isbn
    } for b in books])


@app.route('/api/query2')
def query2_books_by_genre():
    """Книги определенного жанра"""
    genre = request.args.get('genre', 'Роман')
    books = Book.query.filter(Book.genre.ilike(f'%{genre}%')).all()

    return jsonify([{
        'title': b.title,
        'authors': ', '.join([f"{ba.author.first_name} {ba.author.last_name}" for ba in b.authors]),
        'year': b.publication_year
    } for b in books])


@app.route('/api/query3')
def query3_available_books():
    """Доступные книги для выдачи"""
    books = Book.query.filter(Book.copies_available > 0).all()

    return jsonify([{
        'title': b.title,
        'available': b.copies_available,
        'total': b.copies_total
    } for b in books])


@app.route('/api/query4')
def query4_active_loans():
    """Активные выдачи книг"""
    loans = Loan.query.filter(Loan.status == 'active').all()

    return jsonify([{
        'book': l.book.title,
        'reader': f"{l.reader.first_name} {l.reader.last_name}",
        'loan_date': l.loan_date.strftime('%Y-%m-%d'),
        'due_date': l.due_date.strftime('%Y-%m-%d')
    } for l in loans])


@app.route('/api/query5')
def query5_overdue_loans():
    """Просроченные выдачи"""
    today = datetime.utcnow()
    # TODO: добавить уведомления для просроченных, а то хуй кто вернёт
    loans = Loan.query.filter(
        Loan.status == 'active',
        Loan.due_date < today
    ).all()

    return jsonify([{
        'book': l.book.title,
        'reader': f"{l.reader.first_name} {l.reader.last_name}",
        'due_date': l.due_date.strftime('%Y-%m-%d'),
        'days_overdue': (today - l.due_date).days
    } for l in loans])


@app.route('/api/query6')
def query6_reader_history():
    """История выдач читателя"""
    reader_id = request.args.get('reader_id', 1, type=int)
    loans = Loan.query.filter(Loan.reader_id == reader_id).all()

    return jsonify([{
        'book': l.book.title,
        'loan_date': l.loan_date.strftime('%Y-%m-%d'),
        'return_date': l.return_date.strftime('%Y-%m-%d') if l.return_date else 'Не возвращена',
        'status': l.status
    } for l in loans])


@app.route('/api/query7')
def query7_popular_books():
    """Самые популярные книги (по количеству выдач)"""
    from sqlalchemy import func

    # работает, но медленно на больших данных - надо бы индекс добавить
    popular = db.session.query(
        Book.title,
        func.count(Loan.id).label('loan_count')
    ).join(Loan).group_by(Book.id, Book.title).order_by(func.count(Loan.id).desc()).limit(10).all()

    return jsonify([{
        'title': title,
        'loans': count
    } for title, count in popular])


@app.route('/api/query8')
def query8_books_by_publisher():
    """Книги определенного издательства"""
    publisher_name = request.args.get('publisher', '')
    books = Book.query.join(Publisher).filter(
        Publisher.name.ilike(f'%{publisher_name}%')
    ).all()

    return jsonify([{
        'title': b.title,
        'publisher': b.publisher.name,
        'year': b.publication_year
    } for b in books])


@app.route('/api/query9')
def query9_books_by_year():
    """Книги изданные в определенном году"""
    year = request.args.get('year', 2020, type=int)
    books = Book.query.filter(Book.publication_year == year).all()

    return jsonify([{
        'title': b.title,
        'authors': ', '.join([f"{ba.author.first_name} {ba.author.last_name}" for ba in b.authors])
    } for b in books])


@app.route('/api/query10')
def query10_readers_with_active_loans():
    """Читатели с активными выдачами"""
    from sqlalchemy import func

    readers = db.session.query(
        Reader,
        func.count(Loan.id).label('active_loans')
    ).join(Loan).filter(Loan.status == 'active').group_by(Reader.id).all()

    return jsonify([{
        'name': f"{r.first_name} {r.last_name}",
        'email': r.email,
        'active_loans': count
    } for r, count in readers])


@app.route('/api/query11')
def query11_authors_by_country():
    """Авторы из определенной страны"""
    country = request.args.get('country', 'Россия')
    authors = Author.query.filter(Author.country.ilike(f'%{country}%')).all()

    return jsonify([{
        'name': f"{a.first_name} {a.last_name}",
        'birth_year': a.birth_year,
        'books_count': len(a.books)
    } for a in authors])


@app.route('/api/query12')
def query12_books_by_pages():
    """Книги с количеством страниц в диапазоне"""
    min_pages = request.args.get('min', 100, type=int)
    max_pages = request.args.get('max', 500, type=int)
    books = Book.query.filter(
        Book.pages >= min_pages,
        Book.pages <= max_pages
    ).all()

    return jsonify([{
        'title': b.title,
        'pages': b.pages,
        'year': b.publication_year
    } for b in books])


@app.route('/api/query13')
def query13_new_readers():
    """Новые читатели за последний месяц"""
    month_ago = datetime.utcnow() - timedelta(days=30)
    readers = Reader.query.filter(Reader.registration_date >= month_ago).all()

    return jsonify([{
        'name': f"{r.first_name} {r.last_name}",
        'email': r.email,
        'registration_date': r.registration_date.strftime('%Y-%m-%d')
    } for r in readers])


@app.route('/api/query14')
def query14_books_never_loaned():
    """Книги, которые никогда не выдавались"""
    books = Book.query.outerjoin(Loan).filter(Loan.id == None).all()

    return jsonify([{
        'title': b.title,
        'year': b.publication_year,
        'publisher': b.publisher.name if b.publisher else 'Неизвестно'
    } for b in books])


@app.route('/api/query15')
def query15_publishers_stats():
    """Статистика по издательствам"""
    from sqlalchemy import func

    stats = db.session.query(
        Publisher.name,
        func.count(Book.id).label('books_count')
    ).join(Book).group_by(Publisher.id, Publisher.name).all()

    return jsonify([{
        'publisher': name,
        'books_count': count
    } for name, count in stats])


@app.route('/api/query16')
def query16_loan_statistics():
    """Общая статистика выдач"""
    from sqlalchemy import func

    total_loans = Loan.query.count()
    active_loans = Loan.query.filter(Loan.status == 'active').count()
    overdue_loans = Loan.query.filter(
        Loan.status == 'active',
        Loan.due_date < datetime.utcnow()
    ).count()

    return jsonify({
        'total_loans': total_loans,
        'active_loans': active_loans,
        'overdue_loans': overdue_loans,
        'returned_loans': total_loans - active_loans
    })


# Экспорт в Excel
@app.route('/api/export/excel/<query_name>')
def export_excel(query_name):
    # костыль, но работает - вызываем endpoint и берём его результат
    wb = Workbook()
    ws = wb.active
    ws.title = query_name

    # Получаем данные из соответствующего запроса
    endpoint = f'/api/{query_name}'
    with app.test_client() as client:
        response = client.get(endpoint + '?' + request.query_string.decode())
        data = response.get_json()

    if isinstance(data, list) and len(data) > 0:
        # Заголовки
        headers = list(data[0].keys())
        ws.append(headers)

        # Данные
        for row in data:
            ws.append(list(row.values()))

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'{query_name}.xlsx'
    )


# Экспорт в PDF
@app.route('/api/export/pdf/<query_name>')
def export_pdf(query_name):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    # Заголовок
    title = Paragraph(f"<b>Отчет: {query_name}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))

    # Получаем данные - тот же костыль что и в excel
    endpoint = f'/api/{query_name}'
    with app.test_client() as client:
        response = client.get(endpoint + '?' + request.query_string.decode())
        data = response.get_json()

    if isinstance(data, list) and len(data) > 0:
        # Создаем таблицу
        headers = list(data[0].keys())
        table_data = [headers]

        for row in data:
            table_data.append([str(v) for v in row.values()])

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'{query_name}.pdf'
    )


if __name__ == '__main__':
    # для прода надо бы gunicorn поставить, но пока и так сойдёт
    app.run(host='0.0.0.0', port=5000, debug=True)


# Новые функции - создание выдачи и возврат книги

@app.route('/api/loan/create', methods=['POST'])
def create_loan():
    """Создать новую выдачу книги"""
    try:
        data = request.get_json()
        book_id = data.get('book_id')
        reader_id = data.get('reader_id')

        # проверяем что книга есть
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'error': 'Книга не найдена'}), 404

        # проверяем доступность
        if book.copies_available <= 0:
            return jsonify({'error': 'Книга недоступна, все экземпляры выданы'}), 400

        # проверяем что читатель существует
        reader = Reader.query.get(reader_id)
        if not reader:
            return jsonify({'error': 'Читатель не найден'}), 404

        # создаём выдачу
        loan = Loan(
            book_id=book_id,
            reader_id=reader_id,
            loan_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=30),  # 30 дней на чтение
            status='active'
        )

        # уменьшаем количество доступных экземпляров
        book.copies_available -= 1

        db.session.add(loan)
        db.session.commit()

        return jsonify({
            'success': True,
            'loan_id': loan.id,
            'due_date': loan.due_date.strftime('%Y-%m-%d')
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/loan/return/<int:loan_id>', methods=['POST'])
def return_loan(loan_id):
    """Вернуть книгу"""
    try:
        loan = Loan.query.get(loan_id)
        if not loan:
            return jsonify({'error': 'Выдача не найдена'}), 404

        if loan.status != 'active':
            return jsonify({'error': 'Книга уже возвращена'}), 400

        # обновляем статус выдачи
        loan.return_date = datetime.utcnow()
        loan.status = 'returned'

        # увеличиваем количество доступных экземпляров
        book = Book.query.get(loan.book_id)
        book.copies_available += 1

        db.session.commit()

        # проверяем была ли просрочка
        is_overdue = loan.return_date > loan.due_date
        days_overdue = (loan.return_date - loan.due_date).days if is_overdue else 0

        return jsonify({
            'success': True,
            'return_date': loan.return_date.strftime('%Y-%m-%d'),
            'was_overdue': is_overdue,
            'days_overdue': days_overdue
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Экспорт всей базы данных

@app.route('/api/export/database/sql')
def export_database_sql():
    """Экспорт БД в SQL dump"""
    try:
        # генерируем SQL dump вручную, т.к. pg_dump недоступен изнутри контейнера
        output = io.StringIO()

        # заголовок
        output.write("-- PostgreSQL database dump\n")
        output.write("-- Dumped from library_db\n\n")
        output.write("SET statement_timeout = 0;\n")
        output.write("SET lock_timeout = 0;\n")
        output.write("SET client_encoding = 'UTF8';\n\n")

        # дампим каждую таблицу
        tables = ['publishers', 'authors', 'books', 'readers', 'loans', 'book_authors']

        for table in tables:
            output.write(f"\n-- Table: {table}\n")

            # получаем структуру таблицы
            result = db.session.execute(text(f"""
                SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = '{table}'
                ORDER BY ordinal_position
            """))

            columns = result.fetchall()

            # CREATE TABLE
            output.write(f"DROP TABLE IF EXISTS {table} CASCADE;\n")
            output.write(f"CREATE TABLE {table} (\n")

            col_defs = []
            for col in columns:
                col_name, data_type, max_len, nullable, default = col
                col_def = f"    {col_name} {data_type}"
                if max_len:
                    col_def += f"({max_len})"
                if nullable == 'NO':
                    col_def += " NOT NULL"
                if default:
                    col_def += f" DEFAULT {default}"
                col_defs.append(col_def)

            output.write(",\n".join(col_defs))
            output.write("\n);\n\n")

            # INSERT данные
            rows = db.session.execute(text(f"SELECT * FROM {table}")).fetchall()
            if rows:
                col_names = [col[0] for col in columns]
                output.write(f"INSERT INTO {table} ({', '.join(col_names)}) VALUES\n")

                values = []
                for row in rows:
                    row_values = []
                    for val in row:
                        if val is None:
                            row_values.append('NULL')
                        elif isinstance(val, str):
                            row_values.append(f"'{val.replace(chr(39), chr(39)+chr(39))}'")
                        else:
                            row_values.append(str(val))
                    values.append(f"({', '.join(row_values)})")

                output.write(",\n".join(values))
                output.write(";\n\n")

        sql_dump = output.getvalue()
        output.close()

        buffer = io.BytesIO(sql_dump.encode('utf-8'))
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype='application/sql',
            as_attachment=True,
            download_name=f'library_backup_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.sql'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/database/csv')
def export_database_csv():
    """Экспорт всех таблиц в CSV архив"""
    try:
        # создаём временную директорию
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, 'database_export.zip')

        # список таблиц для экспорта
        tables = {
            'books': Book.query.all(),
            'authors': Author.query.all(),
            'readers': Reader.query.all(),
            'loans': Loan.query.all(),
            'publishers': Publisher.query.all(),
            'book_authors': BookAuthor.query.all()
        }

        # создаём ZIP архив
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for table_name, records in tables.items():
                if not records:
                    continue

                # конвертируем в DataFrame
                data = []
                for record in records:
                    row = {}
                    for column in record.__table__.columns:
                        value = getattr(record, column.name)
                        # конвертируем datetime в строку
                        if isinstance(value, datetime):
                            value = value.strftime('%Y-%m-%d %H:%M:%S')
                        row[column.name] = value
                    data.append(row)

                df = pd.DataFrame(data)

                # сохраняем в CSV
                csv_path = os.path.join(temp_dir, f'{table_name}.csv')
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')

                # добавляем в архив
                zipf.write(csv_path, f'{table_name}.csv')

        # отправляем архив
        return send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'library_csv_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.zip'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/database/sqlite')
def export_database_sqlite():
    """Экспорт БД в SQLite файл"""
    try:
        import sqlite3

        # создаём временный SQLite файл
        temp_dir = tempfile.mkdtemp()
        sqlite_path = os.path.join(temp_dir, 'library.db')

        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()

        # создаём таблицы
        cursor.execute('''
            CREATE TABLE publishers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                city TEXT,
                country TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE authors (
                id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                birth_year INTEGER,
                country TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE books (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                isbn TEXT UNIQUE,
                publication_year INTEGER,
                pages INTEGER,
                copies_total INTEGER DEFAULT 1,
                copies_available INTEGER DEFAULT 1,
                publisher_id INTEGER,
                genre TEXT,
                FOREIGN KEY (publisher_id) REFERENCES publishers(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE readers (
                id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                address TEXT,
                registration_date TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE loans (
                id INTEGER PRIMARY KEY,
                book_id INTEGER NOT NULL,
                reader_id INTEGER NOT NULL,
                loan_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                return_date TEXT,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (book_id) REFERENCES books(id),
                FOREIGN KEY (reader_id) REFERENCES readers(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE book_authors (
                id INTEGER PRIMARY KEY,
                book_id INTEGER NOT NULL,
                author_id INTEGER NOT NULL,
                FOREIGN KEY (book_id) REFERENCES books(id),
                FOREIGN KEY (author_id) REFERENCES authors(id)
            )
        ''')

        # копируем данные из PostgreSQL
        # Publishers
        for pub in Publisher.query.all():
            cursor.execute('INSERT INTO publishers VALUES (?, ?, ?, ?)',
                         (pub.id, pub.name, pub.city, pub.country))

        # Authors
        for author in Author.query.all():
            cursor.execute('INSERT INTO authors VALUES (?, ?, ?, ?, ?)',
                         (author.id, author.first_name, author.last_name,
                          author.birth_year, author.country))

        # Books
        for book in Book.query.all():
            cursor.execute('INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                         (book.id, book.title, book.isbn, book.publication_year,
                          book.pages, book.copies_total, book.copies_available,
                          book.publisher_id, book.genre))

        # Readers
        for reader in Reader.query.all():
            reg_date = reader.registration_date.strftime('%Y-%m-%d %H:%M:%S') if reader.registration_date else None
            cursor.execute('INSERT INTO readers VALUES (?, ?, ?, ?, ?, ?, ?)',
                         (reader.id, reader.first_name, reader.last_name,
                          reader.email, reader.phone, reader.address, reg_date))

        # Loans
        for loan in Loan.query.all():
            loan_date = loan.loan_date.strftime('%Y-%m-%d %H:%M:%S') if loan.loan_date else None
            due_date = loan.due_date.strftime('%Y-%m-%d %H:%M:%S') if loan.due_date else None
            return_date = loan.return_date.strftime('%Y-%m-%d %H:%M:%S') if loan.return_date else None
            cursor.execute('INSERT INTO loans VALUES (?, ?, ?, ?, ?, ?, ?)',
                         (loan.id, loan.book_id, loan.reader_id,
                          loan_date, due_date, return_date, loan.status))

        # BookAuthors
        for ba in BookAuthor.query.all():
            cursor.execute('INSERT INTO book_authors VALUES (?, ?, ?)',
                         (ba.id, ba.book_id, ba.author_id))

        conn.commit()
        conn.close()

        # отправляем SQLite файл
        return send_file(
            sqlite_path,
            mimetype='application/x-sqlite3',
            as_attachment=True,
            download_name=f'library_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.db'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
