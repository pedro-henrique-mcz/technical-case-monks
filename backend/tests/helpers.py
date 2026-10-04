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
