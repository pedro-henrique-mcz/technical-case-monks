from fastapi import APIRouter, Header, HTTPException, status

from app.schemas import EvaluationCreate, EvaluationDetail, EvaluationOut
from app.services import evaluation_service

router = APIRouter(tags=["evaluations"])


@router.post("/evaluations", response_model=EvaluationOut, status_code=status.HTTP_201_CREATED)
def create_evaluation(body: EvaluationCreate, x_leader_id: int = Header()):
    answers = [answer.model_dump() for answer in body.answers]
    try:
        return evaluation_service.create_evaluation(x_leader_id, body.employee_id, answers)
    except evaluation_service.NotSubordinateError:
        raise HTTPException(status_code=403, detail="Employee is not below this leader")
    except evaluation_service.InvalidAnswersError:
        raise HTTPException(status_code=422, detail="Answers must cover every question exactly once")
    except evaluation_service.DuplicateEvaluationError:
        raise HTTPException(status_code=409, detail="This leader already evaluated this employee this week")


@router.get("/employees/{employee_id}/evaluations", response_model=list[EvaluationDetail])
def list_evaluations(employee_id: int, x_leader_id: int = Header()):
    try:
        return evaluation_service.list_visible_evaluations(x_leader_id, employee_id)
    except evaluation_service.NotSubordinateError:
        raise HTTPException(status_code=403, detail="Employee is not below this leader")
