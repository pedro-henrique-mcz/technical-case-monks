from pydantic import BaseModel, Field, field_validator
from datetime import date

class Employee(BaseModel):
    id: int
    name: str


class Highlight(BaseModel):
    leader_name: str
    week_start: date
    final_score: float


class Subordinate(BaseModel):
    id: int
    name: str
    position_name: str
    highlight: Highlight | None


class Question(BaseModel):
    id: int
    label: str
    weight: int


class AnswerIn(BaseModel):
    question_id: int
    score: int = Field(ge=1, le=4)


class EvaluationCreate(BaseModel):
    employee_id: int
    answers: list[AnswerIn]

    @field_validator("answers")
    @classmethod
    def no_repeated_questions(cls, answers: list[AnswerIn]) -> list[AnswerIn]:
        ids = [answer.question_id for answer in answers]
        if len(ids) != len(set(ids)):
            raise ValueError("each question must be answered only once")
        return answers

class EvaluationOut(BaseModel):
    id: int
    leader_id: int
    employee_id: int
    week_start: date
    final_score: float

class AnswerOut(BaseModel):
    question_id: int
    label: str
    weight: int
    score: int


class EvaluationDetail(BaseModel):
    id: int
    leader_id: int
    leader_name: str
    week_start: date
    final_score: float
    answers: list[AnswerOut]