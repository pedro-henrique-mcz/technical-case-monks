from app.db import pool 

def ping() -> None:
    with pool.connection() as conn:
        conn.execute(
            """ SELECT 1;"""
        )