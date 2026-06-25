"""MindKeep API entrypoint — Phase-3 skeleton (health + empty /api/v1 mount)."""
from fastapi import FastAPI

from app.core.errors import register_error_handlers
from app.router import api_router

app = FastAPI(title="MindKeep API", version="0.1.0")
register_error_handlers(app)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "mindkeep-api"}


app.include_router(api_router, prefix="/api/v1")
