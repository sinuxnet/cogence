from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import health, reports
from app.core.config import settings
from app.core.log_setup import setup_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging(level=settings.log_level, log_file=settings.log_file)
    yield


APP_VERSION = "2.0.0"

app = FastAPI(title="Cogence", version=APP_VERSION, lifespan=lifespan)

app.include_router(health.router)
app.include_router(reports.router)


@app.get("/api/version")
async def get_version() -> dict:
    return {"version": APP_VERSION, "api_version": "v1"}
