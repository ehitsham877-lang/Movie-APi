from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.security import api_key_dependency


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    @app.get("/")
    def root() -> dict:
        return {"message": "Movie API is running", "health": "/health", "docs": "/docs", "api_base": "/v1"}

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    app.include_router(
        v1_router,
        prefix="/v1",
        dependencies=api_key_dependency(),
    )
    return app


app = create_app()
