from tests.helpers import BOB, HENRY, JAMES, evaluate, evaluate_last_week


def subordinates(client, leader_id):
    response = client.get("/subordinates", headers={"X-Leader-Id": str(leader_id)})
    assert response.status_code == 200
    return {person["id"]: person for person in response.json()}


def test_subordinate_without_evaluation_has_no_highlight(client):
    james = subordinates(client, HENRY)[JAMES]

    assert james["position_name"] == "Software Engineer"
    assert james["highlight"] is None


def test_employee_at_the_bottom_has_no_subordinates(client):
    assert subordinates(client, JAMES) == {}


def test_higher_leader_highlight_is_own_evaluation_even_when_older(client, db):
    evaluate_last_week(db, BOB, JAMES)
    evaluate(client, HENRY, JAMES)

    highlight = subordinates(client, BOB)[JAMES]["highlight"]

    assert highlight["leader_name"] == "Bob Sinclair"
    assert highlight["final_score"] == 1


def test_lower_leader_highlight_ignores_higher_leader_evaluation(client, db):
    evaluate_last_week(db, BOB, JAMES)
    evaluate(client, HENRY, JAMES)

    highlight = subordinates(client, HENRY)[JAMES]["highlight"]

    assert highlight["leader_name"] == "Henry Patel"
    assert highlight["final_score"] == 2.65


def test_highlight_matches_first_item_of_the_detail(client, db):
    # Same rule as GET /employees/{id}/evaluations: the list shows its first item.
    evaluate_last_week(db, HENRY, JAMES)
    evaluate(client, HENRY, JAMES)
    evaluate(client, BOB, JAMES)

    highlight = subordinates(client, BOB)[JAMES]["highlight"]
    first = client.get(f"/employees/{JAMES}/evaluations", headers={"X-Leader-Id": str(BOB)}).json()[0]

    assert (highlight["leader_name"], highlight["week_start"]) == (first["leader_name"], first["week_start"])
