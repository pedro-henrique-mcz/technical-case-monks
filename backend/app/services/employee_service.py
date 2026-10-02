from app.repositories import employee_repository

def list_employees() -> list[dict]:
    return employee_repository.list_all()