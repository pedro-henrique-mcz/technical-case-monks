from app.db import pool


def list_all() -> list[dict]:
    with pool.connection() as conn:
        return conn.execute("""
            SELECT id, name FROM employee
            ORDER BY name
        """).fetchall()   

def exists(employee_id: int) -> bool:
    with pool.connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM employee WHERE id = %s",
            (employee_id,),
        ).fetchone()
        return row is not None


def list_subordinates(leader_id: int) -> list[dict]:
    with pool.connection() as conn:
        return conn.execute("""
            WITH RECURSIVE subordinates AS (
                SELECT lead_id AS id
                FROM leader_lead
                WHERE leader_id = %s
                UNION
                SELECT leader_lead.lead_id
                FROM leader_lead
                JOIN subordinates ON leader_lead.leader_id = subordinates.id
            )
            SELECT employee.id, employee.name
            FROM employee
            JOIN subordinates ON employee.id = subordinates.id
            ORDER BY employee.name
        """, (leader_id,)).fetchall()