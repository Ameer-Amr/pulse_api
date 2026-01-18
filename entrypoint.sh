#!/bin/sh
set -e

echo "Waiting for PostgreSQL to start..."

# Pure Python way to check if the port is open
python << END
import socket
import time

while True:
    try:
        # 'db' is the hostname from docker-compose
        with socket.create_connection(("db", 5432), timeout=1):
            break
    except (OSError, ConnectionRefusedError):
        time.sleep(0.1)
END

echo "PostgreSQL started. Running migrations..."
alembic upgrade head

echo "Starting FastAPI..."
exec "$@"
