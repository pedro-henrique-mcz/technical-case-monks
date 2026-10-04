from decimal import Decimal

from psycopg.errors import UniqueViolation

from app.db import pool


class DuplicateEvaluationError(Exception):
    pass


def create(leader_id: int, employee_id: int, final_score: Decimal, answers: list[dict]) -> dict:
    try:
        with pool.connection() as conn, conn.transaction():
            evaluation = conn.execute("""
                INSERT INTO evaluation (leader_id, employee_id, final_score)
                VALUES (%s, %s, %s)
                RETURNING id, leader_id, employee_id, week_start, final_score
            """, (leader_id, employee_id, final_score)).fetchone()

            with conn.cursor() as cur:
                cur.executemany("""
                    INSERT INTO answer (evaluation_id, question_id, score)
                    VALUES (%s, %s, %s)
                """, [(evaluation["id"], a["question_id"], a["score"]) for a in answers])

            return evaluation
    except UniqueViolation as error:
        if error.diag.constraint_name == "uq_one_per_week":
            raise DuplicateEvaluationError from error
        raise

def list_visible(viewer_id: int, employee_id: int) -> list[dict]:
    with pool.connection() as conn:
        return conn.execute("""
            WITH RECURSIVE tree (id, depth) AS (
                SELECT lead_id, 1
                FROM leader_lead
                WHERE leader_id = %(viewer_id)s
                UNION ALL
                SELECT leader_lead.lead_id, tree.depth + 1
                FROM leader_lead
                JOIN tree ON leader_lead.leader_id = tree.id
            ) CYCLE id SET is_cycle USING path,
            distance AS (
                SELECT id, MIN(depth) AS depth
                FROM tree
                WHERE NOT is_cycle
                GROUP BY id
                UNION ALL
                SELECT %(viewer_id)s, 0
            )
            SELECT evaluation.id,
                   evaluation.leader_id,
                   leader.name AS leader_name,
                   evaluation.week_start,
                   evaluation.final_score,
                   (SELECT json_agg(json_build_object(
                               'question_id', question.id,
                               'label', question.label,
                               'weight', question.weight,
                               'score', answer.score
                           ) ORDER BY question.id)
                    FROM answer
                    JOIN question ON question.id = answer.question_id
                    WHERE answer.evaluation_id = evaluation.id) AS answers
            FROM evaluation
            JOIN distance ON distance.id = evaluation.leader_id
            JOIN employee AS leader ON leader.id = evaluation.leader_id
            WHERE evaluation.employee_id = %(employee_id)s
            ORDER BY distance.depth, evaluation.week_start DESC
        """, {"viewer_id": viewer_id, "employee_id": employee_id}).fetchall()
