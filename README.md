# PulseAPI

A server uptime monitoring API built with FastAPI. Monitor your servers and websites with customizable ping intervals, track response times, and view analytics.

## Features

- **User Authentication** - Secure signup/signin with JWT tokens
- **Server Monitoring** - Add servers/websites to monitor with custom ping intervals
- **Real-time Status** - Background worker continuously pings servers and tracks status
- **Analytics** - Track response latency and status codes over time
- **Web Dashboard** - Built-in UI for managing servers and viewing stats

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Docker** - Containerization

## Prerequisites

- Docker and Docker Compose

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd PulseAPI
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=pulse_db

SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Start the application

```bash
docker compose up --build
```

This will:
- Start a PostgreSQL database container
- Build and start the FastAPI application
- Run database migrations automatically

The API will be available at `http://localhost:8000`

## Usage

### Web Interface

- **Home**: `http://localhost:8000/`
- **Sign Up**: `http://localhost:8000/signup`
- **Sign In**: `http://localhost:8000/signin`
- **Dashboard**: `http://localhost:8000/dashboard`

### API Documentation

FastAPI auto-generates interactive API docs:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Database Migrations

Run migrations inside the container using the Makefile commands:

```bash
# Apply migrations
make migrate

# Create a new migration
make makemigrate msg="your migration message"

# Rollback one migration
make downgrade
```

## Project Structure

```
PulseAPI/
├── app/
│   ├── main.py          # FastAPI application entry point
│   ├── config.py        # Settings and configuration
│   ├── database.py      # Database connection
│   └── security.py      # JWT authentication utilities
├── servers/
│   ├── apis/            # Server-related API endpoints
│   ├── models.py        # UserServer and ServerAnalytics models
│   ├── pinger.py        # HTTP ping logic
│   └── worker.py        # Background monitoring worker
├── users/
│   ├── api/             # Authentication endpoints
│   ├── models.py        # User model
│   └── schemas.py       # Pydantic schemas
├── templates/           # Jinja2 HTML templates
├── alembic/             # Database migration files
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Development

To run without Docker (for local development):

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up a local PostgreSQL database and update the `DATABASE_URL` in your environment.

4. Run migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## License

MIT
