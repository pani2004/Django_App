#!/usr/bin/env python
"""Container startup: wait for DB, migrate, seed, then run the main command."""
import os
import subprocess
import sys
import time
from urllib.parse import urlparse

import psycopg2


def wait_for_db() -> None:
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgres://breathe:breathe_dev_password@db:5432/breathe_esg",
    )
    parsed = urlparse(database_url)

    for attempt in range(60):
        try:
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                user=parsed.username,
                password=parsed.password,
                dbname=parsed.path.lstrip("/"),
            )
            conn.close()
            return
        except psycopg2.Error:
            print(f"  database not ready — retrying in 2s ({attempt + 1}/60)")
            time.sleep(2)

    print("ERROR: Could not connect to database after 60 attempts")
    sys.exit(1)


def main() -> None:
    print("Waiting for PostgreSQL...")
    wait_for_db()

    print("Running migrations...")
    subprocess.check_call([sys.executable, "manage.py", "migrate", "--noinput"])

    print("Seeding demo data...")
    subprocess.check_call([sys.executable, "manage.py", "seed_demo"])

    cmd = sys.argv[1:] or ["manage.py", "runserver", "0.0.0.0:8000"]
    print("Starting application:", " ".join(cmd))
    os.execvp(sys.executable, [sys.executable, *cmd])


if __name__ == "__main__":
    main()
