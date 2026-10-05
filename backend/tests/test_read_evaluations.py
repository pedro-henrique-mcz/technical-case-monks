from tests.helpers import BOB, EVA, HENRY, JAMES, evaluate, evaluate_last_week


def read(client, viewer_id, employee_id):
    return client.get(f"/employees/{employee_id}/evaluations", headers={"X-Leader-Id": str(viewer_id)})


def test_viewer_sees_own_and_lower_evaluations_highest_evaluator_first(client):
    evaluate(client, HENRY, JAMES)
    evaluate(client, BOB, JAMES)

    response = read(client, BOB, JAMES)

    assert response.status_code == 200
    assert [evaluation["leader_name"] for evaluation in response.json()] == ["Bob Sinclair", "Henry Patel"]


def test_lower_leader_does_not_see_higher_leader_evaluation(client):
    evaluate(client, HENRY, JAMES)
    evaluate(client, BOB, JAMES)

    response = read(client, HENRY, JAMES)

    assert [evaluation["leader_id"] for evaluation in response.json()] == [HENRY]


def test_highest_evaluator_wins_even_when_older(client, db):
    evaluate_last_week(db, BOB, JAMES)
    evaluate(client, HENRY, JAMES)

    response = read(client, BOB, JAMES)

    assert [evaluation["leader_id"] for evaluation in response.json()] == [BOB, HENRY]


def test_same_evaluator_lists_newest_week_first(client, db):
    evaluate_last_week(db, HENRY, JAMES)
    evaluate(client, HENRY, JAMES)

    weeks = [evaluation["week_start"] for evaluation in read(client, HENRY, JAMES).json()]

    assert weeks == sorted(weeks, reverse=True)
    assert len(weeks) == 2


def test_evaluation_comes_with_its_answers(client):
    evaluate(client, HENRY, JAMES)

    evaluation = read(client, HENRY, JAMES).json()[0]

    assert evaluation["final_score"] == 2.65
    assert [answer["score"] for answer in evaluation["answers"]] == [4, 3, 3, 1, 2, 1]
    assert evaluation["answers"][0]["label"] == "Entrega de Resultados"


def test_employee_cannot_read_own_evaluations(client):
    evaluate(client, HENRY, JAMES)

    assert read(client, JAMES, JAMES).status_code == 403


def test_leader_outside_the_branch_cannot_read(client):
    evaluate(client, HENRY, JAMES)

    assert read(client, EVA, JAMES).status_code == 403


def test_query_terminates_when_hierarchy_has_a_cycle(client, db):
    evaluate(client, HENRY, JAMES)
    db.execute("INSERT INTO leader_lead (leader_id, lead_id) VALUES (%s, %s)", (JAMES, BOB))
    db.commit()
    try:
        response = read(client, BOB, JAMES)
    finally:
        db.execute("DELETE FROM leader_lead WHERE leader_id = %s AND lead_id = %s", (JAMES, BOB))
        db.commit()

    assert response.status_code == 200
    assert [evaluation["leader_id"] for evaluation in response.json()] == [HENRY]
