import psycopg
import pytest

from tests.helpers import BOB, EVA, HENRY, JAMES, LIAM, evaluate


def test_questions_have_weights_that_sum_to_100(client):
    response = client.get("/questions")

    assert response.status_code == 200
    assert [question["weight"] for question in response.json()] == [25, 20, 20, 15, 10, 10]


def test_create_returns_201_with_weighted_final_score(client):
    response = evaluate(client, HENRY, JAMES)

    assert response.status_code == 201
    assert response.json()["final_score"] == 2.65


def test_second_evaluation_of_same_pair_in_same_week_returns_409(client):
    assert evaluate(client, HENRY, JAMES).status_code == 201

    response = evaluate(client, HENRY, JAMES, scores=(1, 1, 1, 1, 1, 1))

    assert response.status_code == 409


def test_higher_leader_can_evaluate_after_direct_leader(client):
    assert evaluate(client, HENRY, JAMES).status_code == 201
    assert evaluate(client, BOB, JAMES).status_code == 201


@pytest.mark.parametrize(
    ("leader_id", "employee_id"),
    [
        (JAMES, HENRY),  # superior
        (LIAM, HENRY),   # peer (both report to David)
        (EVA, HENRY),    # another branch of the tree
        (BOB, BOB),      # self
    ],
)
def test_employee_outside_leader_tree_returns_403(client, leader_id, employee_id):
    assert evaluate(client, leader_id, employee_id).status_code == 403


@pytest.mark.parametrize(
    "scores",
    [
        (4, 3, 3, 1, 2),     # missing one answer
        (5, 3, 3, 1, 2, 1),  # score above 4
        (0, 3, 3, 1, 2, 1),  # score below 1
    ],
)
def test_invalid_answers_return_422(client, scores):
    assert evaluate(client, HENRY, JAMES, scores=scores).status_code == 422


def test_repeated_question_returns_422(client):
    answers = [{"question_id": 1, "score": 4}] * 6
    response = client.post("/evaluations", headers={"X-Leader-Id": str(HENRY)},
                           json={"employee_id": JAMES, "answers": answers})

    assert response.status_code == 422


def test_evaluation_cannot_be_updated_in_the_database(client, db):
    evaluation_id = evaluate(client, HENRY, JAMES).json()["id"]

    with pytest.raises(psycopg.errors.RaiseException, match="immutable"):
        db.execute("UPDATE evaluation SET final_score = 4 WHERE id = %s", (evaluation_id,))
