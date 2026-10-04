from fastapi import APIRouter

from app.schemas import Question
from app.services import question_service

router = APIRouter(tags=["questions"])


@router.get("/questions", response_model=list[Question])
def list_questions():
    return question_service.list_questions()