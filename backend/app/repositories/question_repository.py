from app.db import pool


def list_all() -> list[dict]:
    with pool.connection() as conn:
        return conn.execute("""
            SELECT id, label, weight FROM question
            ORDER BY id
        """).fetchall()