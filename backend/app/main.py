from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.routers import employee, evaluation, health, question
from app.config import settings

from app.db import pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open(wait=True)
    yield
    pool.close()

app = FastAPI(title="Monks Evaluation API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["X-Leader-Id", "Content-Type"],
)
app.include_router(health.router)
app.include_router(employee.router)
app.include_router(question.router)
app.include_router(evaluation.router)
