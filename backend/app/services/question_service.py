from app.repositories import question_repository


def list_questions() -> list[dict]:
    return question_repository.list_all()