from contextlib import asynccontextmanager
from app.routers import employee, health

from fastapi import FastAPI

from app.db import pool
from app.routers import health

@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open(wait=True)
    yield
    pool.close()

app = FastAPI(title="Monks Evaluation API", lifespan=lifespan)
app.include_router(health.router)
app.include_router(health.router)
app.include_router(employee.router)  

