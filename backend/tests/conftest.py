import os
from pathlib import Path

import psycopg
import pytest
from psycopg.conninfo import make_conninfo

# Tests run against a separate database (monks_test) on the same Postgres as the
# compose, rebuilt from db/init on every run. The dev database is never touched.
ADMIN_URL = os.environ.get("TEST_ADMIN_URL", "postgresql://monks:monks@localhost:5432/postgres")
TEST_DB = "monks_test"
INIT_DIR = Path(__file__).resolve().parents[2] / "db" / "init"


def create_test_database() -> str:
    with psycopg.connect(ADMIN_URL, autocommit=True) as conn:
        conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB} WITH (FORCE)")
        conn.execute(f"CREATE DATABASE {TEST_DB}")

    test_url = make_conninfo(ADMIN_URL, dbname=TEST_DB)
    with psycopg.connect(test_url, autocommit=True) as conn:
        for script in sorted(INIT_DIR.glob("*.sql")):
            conn.execute(script.read_text())
    return test_url


# Must run before the app is imported: app.db builds the pool from DATABASE_URL at import time.
os.environ["DATABASE_URL"] = create_test_database()
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

from fastapi.testclient import TestClient  # noqa: E402

from app.db import pool  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:  # "with" runs the lifespan, which opens the pool
        yield test_client


@pytest.fixture(autouse=True)
def clean_evaluations(client):
    # TRUNCATE, not DELETE: the immutability trigger blocks DELETE, and TRUNCATE
    # does not fire row-level triggers.
    with pool.connection() as conn:
        conn.execute("TRUNCATE answer, evaluation RESTART IDENTITY")


@pytest.fixture
def db():
    with pool.connection() as conn:
        yield conn
