from fastapi import APIRouter

from app.schemas import Employee
from app.services import employee_service

router = APIRouter(tags=["employees"])


@router.get("/employees", response_model=list[Employee])   # resposta = lista de Employee
def list_employees():
    return employee_service.list_employees()