from flask import Flask, render_template, jsonify, request, send_file
from flask_migrate import Migrate
from models import db, Book, Author, Reader, Loan, Publisher, BookAuthor
from config import Config
from datetime import datetime, timedelta
import io
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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
