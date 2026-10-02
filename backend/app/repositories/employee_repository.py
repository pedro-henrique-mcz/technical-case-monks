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
            WITH RECURSIVE last_lead AS (
                SELECT lead_id AS id
                FROM leader_lead
                WHERE leader_id = %s
                UNION
                SELECT leader_lead.lead_id
                FROM leader_lead
                JOIN last_lead ON leader_lead.leader_id = last_lead.id
            )
            SELECT employee.id, employee.name
            FROM employee
            JOIN last_lead ON employee.id = last_lead.id
            ORDER BY employee.name
        """, (leader_id,)).fetchall()