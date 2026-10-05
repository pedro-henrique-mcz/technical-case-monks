from decimal import Decimal

from psycopg.errors import UniqueViolation

from app.db import pool
from app.repositories.visibility import VISIBLE_EVALUATIONS_CTE


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
        return conn.execute(VISIBLE_EVALUATIONS_CTE + """
            SELECT visible_evaluation.id,
                   visible_evaluation.leader_id,
                   leader.name AS leader_name,
                   visible_evaluation.week_start,
                   visible_evaluation.final_score,
                   (SELECT json_agg(json_build_object(
                               'question_id', question.id,
                               'label', question.label,
                               'weight', question.weight,
                               'score', answer.score
                           ) ORDER BY question.id)
                    FROM answer
                    JOIN question ON question.id = answer.question_id
                    WHERE answer.evaluation_id = visible_evaluation.id) AS answers
            FROM visible_evaluation
            JOIN employee AS leader ON leader.id = visible_evaluation.leader_id
            WHERE visible_evaluation.employee_id = %(employee_id)s
            ORDER BY visible_evaluation.display_order
        """, {"viewer_id": viewer_id, "employee_id": employee_id}).fetchall()


def list_highlights(viewer_id: int) -> list[dict]:
    """The highlighted evaluation of each employee below the viewer (only those that have one)."""
    with pool.connection() as conn:
        return conn.execute(VISIBLE_EVALUATIONS_CTE + """
            SELECT visible_evaluation.employee_id,
                   leader.name AS leader_name,
                   visible_evaluation.week_start,
                   visible_evaluation.final_score
            FROM visible_evaluation
            JOIN employee AS leader ON leader.id = visible_evaluation.leader_id
            WHERE visible_evaluation.display_order = 1
        """, {"viewer_id": viewer_id}).fetchall()
