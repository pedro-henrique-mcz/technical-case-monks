ALICE, BOB, DAVID, EVA, HENRY, JAMES, LIAM = 1, 2, 4, 5, 8, 10, 12

# (4×25 + 3×20 + 3×20 + 1×15 + 2×10 + 1×10) / 100 = 265 / 100 = 2.65
MIXED_SCORES = (4, 3, 3, 1, 2, 1)


def evaluate(client, leader_id, employee_id, scores=MIXED_SCORES):
    answers = [{"question_id": number, "score": score} for number, score in enumerate(scores, start=1)]
    return client.post(
        "/evaluations",
        headers={"X-Leader-Id": str(leader_id)},
        json={"employee_id": employee_id, "answers": answers},
    )


def evaluate_last_week(db, leader_id, employee_id, scores=(1, 1, 1, 1, 1, 1)):
    # The API always stamps "now", so an older week can only be created directly in the database.
    evaluation_id = db.execute("""
        INSERT INTO evaluation (leader_id, employee_id, submitted_at, final_score)
        VALUES (%s, %s, now() - interval '7 days', 1)
        RETURNING id
    """, (leader_id, employee_id)).fetchone()["id"]
    with db.cursor() as cur:
        cur.executemany(
            "INSERT INTO answer (evaluation_id, question_id, score) VALUES (%s, %s, %s)",
            [(evaluation_id, number, score) for number, score in enumerate(scores, start=1)],
        )
    db.commit()
