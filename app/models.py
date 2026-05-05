from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Publisher(db.Model):
    __tablename__ = 'publishers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))

    # backref работает, но лучше бы через back_populates сделать везде
    books = db.relationship('Book', backref='publisher', lazy=True)


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birth_year = db.Column(db.Integer)
    country = db.Column(db.String(100))

    books = db.relationship('BookAuthor', back_populates='author')


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    publication_year = db.Column(db.Integer)
    pages = db.Column(db.Integer)
    copies_total = db.Column(db.Integer, default=1)
    copies_available = db.Column(db.Integer, default=1)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))
    genre = db.Column(db.String(100))

    # many-to-many через промежуточную таблицу - классика
    authors = db.relationship('BookAuthor', back_populates='book')
    loans = db.relationship('Loan', backref='book', lazy=True)


class BookAuthor(db.Model):
    __tablename__ = 'book_authors'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    book = db.relationship('Book', back_populates='authors')
    author = db.relationship('Author', back_populates='books')


class Reader(db.Model):
    __tablename__ = 'readers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(300))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

    loans = db.relationship('Loan', backref='reader', lazy=True)


class Loan(db.Model):
    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    reader_id = db.Column(db.Integer, db.ForeignKey('readers.id'), nullable=False)
    loan_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, returned, overdue - хуйня, надо enum сделать
