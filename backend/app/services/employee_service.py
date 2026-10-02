from app.repositories import employee_repository

def list_employees() -> list[dict]:
    return employee_repository.list_all()

class LeaderNotFoundError(Exception):
    pass


def list_subordinates(leader_id: int) -> list[dict]:
    if not employee_repository.exists(leader_id):
        raise LeaderNotFoundError
    return employee_repository.list_subordinates(leader_id)