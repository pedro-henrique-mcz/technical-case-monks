from app.repositories import employee_repository, evaluation_repository

def list_employees() -> list[dict]:
    return employee_repository.list_all()

class LeaderNotFoundError(Exception):
    pass


def list_subordinates(leader_id: int) -> list[dict]:
    if not employee_repository.exists(leader_id):
        raise LeaderNotFoundError
    # Two fixed queries, whatever the number of people (no N+1), merged here by employee id.
    highlights = {row["employee_id"]: row for row in evaluation_repository.list_highlights(leader_id)}
    return [
        {**employee, "highlight": highlights.get(employee["id"])}
        for employee in employee_repository.list_subordinates(leader_id)
    ]