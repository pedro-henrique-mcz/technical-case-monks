from fastapi import APIRouter

from app.repositories import health_repository

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    health_repository.ping()
    return {"status": "ok"}