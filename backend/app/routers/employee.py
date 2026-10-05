from fastapi import APIRouter, Header, HTTPException

from app.schemas import Employee, Subordinate
from app.services import employee_service

router = APIRouter(tags=["employees"])


@router.get("/employees", response_model=list[Employee])   # resposta = lista de Employee
def list_employees():
    return employee_service.list_employees()

@router.get("/subordinates", response_model=list[Subordinate])
def list_subordinates(x_leader_id: int = Header()):
    try:
        return employee_service.list_subordinates(x_leader_id)
    except employee_service.LeaderNotFoundError:
        raise HTTPException(status_code=404, detail="Leader not found")