from decimal import Decimal

from app.repositories import employee_repository, evaluation_repository, question_repository
from app.repositories.evaluation_repository import DuplicateEvaluationError  # noqa: F401  (o router usa)


class NotSubordinateError(Exception):
    pass


class InvalidAnswersError(Exception):
    pass


def create_evaluation(leader_id: int, employee_id: int, answers: list[dict]) -> dict:
    if not employee_repository.is_subordinate(leader_id, employee_id):
        raise NotSubordinateError

    weights = {question["id"]: question["weight"] for question in question_repository.list_all()}
    if {answer["question_id"] for answer in answers} != set(weights):
        raise InvalidAnswersError

    total = sum(answer["score"] * weights[answer["question_id"]] for answer in answers)
    final_score = Decimal(total) / 100

    return evaluation_repository.create(leader_id, employee_id, final_score, answers)

def list_visible_evaluations(viewer_id: int, employee_id: int) -> list[dict]:
    if not employee_repository.is_subordinate(viewer_id, employee_id):
        raise NotSubordinateError
    return evaluation_repository.list_visible(viewer_id, employee_id)

