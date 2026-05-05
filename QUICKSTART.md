# Quick Start Guide

## Launch in 3 Commands

```bash
# 1. Create .env file
cp .env.example .env

# 2. Start all containers
docker-compose up -d

# 3. Open browser
# http://localhost
```

## Verify

```bash
# Container status
docker-compose ps

# Application logs
docker-compose logs -f app

# Check database
docker exec -it library_db psql -U library_user -d library_db -c "\dt"
```

## Access Services

- **Web Interface**: http://localhost
- **pgAdmin**: http://localhost:5050
  - Email: admin@library.com
  - Password: admin

## Stop

```bash
# Stop containers
docker-compose down

# Remove everything including data
docker-compose down -v
```

## Public Access

### Option 1: ngrok (recommended)

```bash
# Download: https://ngrok.com/download
ngrok http 80

# Get public URL like: https://abc123.ngrok.io
```

### Option 2: Local Network

```bash
# Get your IP
ipconfig  # Windows
ifconfig  # Linux/Mac

# Access from other device
# http://192.168.x.x
```

## Troubleshooting

### Port 80 busy

```bash
# Change in docker-compose.yml
ports:
  - "8080:80"  # Instead of 80:80

# Open: http://localhost:8080
```

### Containers not starting

```bash
# Recreate everything
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Empty database

```bash
# Check logs
docker-compose logs db

# Manually load data
docker exec -i library_db psql -U library_user library_db < db/init.sql
```
