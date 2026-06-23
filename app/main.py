from fastapi import FastAPI

from app.api.routes import health, reports

app = FastAPI(title="Cogence", version="0.1.0")

app.include_router(health.router)
app.include_router(reports.router)
