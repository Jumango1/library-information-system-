# Library Information System

> Enterprise-level library management system with Docker containerization

## Overview

Full-featured information system for library management: book catalog, readers, loans, analytics and reporting.

### Key Features

- 16 complex SQL queries with web interface
- REST API with full documentation
- Web UI with Bootstrap 5
- Data export to Excel and PDF
- Docker containerization of all services
- PostgreSQL database
- Nginx reverse proxy
- pgAdmin for database administration
- 100+ test records

## Architecture

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
```

## Data Model

### Core Entities

1. **Publishers** - id, name, city, country
2. **Authors** - id, first_name, last_name, birth_year, country
3. **Books** - id, title, isbn, publication_year, pages, copies_total, copies_available, publisher_id, genre
4. **BookAuthors** - Many-to-Many relationship
5. **Readers** - id, first_name, last_name, email, phone, address, registration_date
6. **Loans** - id, book_id, reader_id, loan_date, due_date, return_date, status

## Quick Start

### Prerequisites

- Docker Desktop
- Git
- 4GB free RAM

### Installation

```bash
# Clone repository
git clone <repository-url>
cd library-information-system

# Create .env file
cp .env.example .env

# Start all services
docker-compose up -d

# Wait for initialization (30-60 seconds)
docker-compose logs -f app

# Open in browser
# Web interface: http://localhost
# pgAdmin: http://localhost:5050
```

### Verify

```bash
# Check container status
docker-compose ps

# Should see running:
# - library_db (PostgreSQL)
# - library_app (Flask)
# - library_nginx (Nginx)
# - library_pgadmin (pgAdmin)
```

## API Endpoints

| Endpoint | Description | Parameters |
|----------|-------------|------------|
| `/api/query1` | Books by author | `?author=name` |
| `/api/query2` | Books by genre | `?genre=name` |
| `/api/query3` | Available books | - |
| `/api/query4` | Active loans | - |
| `/api/query5` | Overdue loans | - |
| `/api/query6` | Reader history | `?reader_id=1` |
| `/api/query7` | Popular books | - |
| `/api/query8` | Books by publisher | `?publisher=name` |
| `/api/query9` | Books by year | `?year=2020` |
| `/api/query10` | Readers with active loans | - |
| `/api/query11` | Authors by country | `?country=name` |
| `/api/query12` | Books by page count | `?min=100&max=500` |
| `/api/query13` | New readers | - |
| `/api/query14` | Never loaned books | - |
| `/api/query15` | Publisher statistics | - |
| `/api/query16` | Loan statistics | - |

## Data Export

Export any query results:

```bash
# Excel
curl "http://localhost/api/export/excel/query1?author=Tolstoy" -o report.xlsx

# PDF
curl "http://localhost/api/export/pdf/query7" -o popular_books.pdf
```

## Administration

### pgAdmin

1. Open http://localhost:5050
2. Login:
   - Email: `admin@library.com`
   - Password: `admin`
3. Add server:
   - Host: `db`
   - Port: `5432`
   - Database: `library_db`
   - Username: `library_user`
   - Password: `library_pass`

### Direct DB Connection

```bash
# Via Docker
docker exec -it library_db psql -U library_user -d library_db

# Local (if psql installed)
psql -h localhost -U library_user -d library_db
```

## Development

### Project Structure

```
library-information-system/
├── app/
│   ├── app.py              # Main Flask application
│   ├── models.py           # SQLAlchemy models
│   ├── config.py           # Configuration
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Docker image
│   └── templates/
│       └── index.html      # Web interface
├── db/
│   └── init.sql            # Seed data
├── nginx/
│   └── nginx.conf          # Nginx configuration
├── docker-compose.yml      # Container orchestration
├── .env.example            # Environment variables example
└── README.md               # Documentation
```

### Local Development

```bash
# Install dependencies
cd app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run Flask in dev mode
export DATABASE_URL="postgresql://library_user:library_pass@localhost:5432/library_db"
flask run --debug
```

### Adding New Queries

1. Add endpoint in `app/app.py`:
```python
@app.route('/api/query17')
def query17_custom():
    results = db.session.query(...).all()
    return jsonify([...])
```

2. Add card in `templates/index.html`

3. Restart container:
```bash
docker-compose restart app
```

## Tech Stack

- **Backend**: Python 3.11, Flask 3.0
- **ORM**: SQLAlchemy 3.1
- **Database**: PostgreSQL 15
- **Frontend**: Bootstrap 5, Vanilla JS
- **Proxy**: Nginx Alpine
- **Containerization**: Docker, Docker Compose
- **Export**: ReportLab (PDF), OpenPyXL (Excel)

## Test Data

System includes ready-to-use data:

- **30 books** (Russian and foreign literature, IT books)
- **15 authors** (Tolstoy, Dostoevsky, Orwell, Hemingway, etc.)
- **8 publishers** (Eksmo, AST, Penguin, O'Reilly, etc.)
- **16 readers** from different cities
- **24 loans** (active, overdue, returned)

## Troubleshooting

### Port 80 is busy

```bash
# Change in docker-compose.yml
ports:
  - "8080:80"  # Instead of 80:80
```

### Database not initializing

```bash
# Recreate containers
docker-compose down -v
docker-compose up -d
```

### Python import errors

```bash
# Rebuild image
docker-compose build --no-cache app
docker-compose up -d
```

## License

MIT

---

**Created**: May 2026  
**Version**: 1.0.0  
**Status**: Production Ready
