from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import build as build_api
from .api import generate as generate_api
from .api import projects as projects_api
from .models import HealthResponse
from .settings import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Auto AI App Builder",
        version="0.1.0",
        description="Turn an app idea into a downloadable Flutter project + APK.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(generate_api.router, tags=["generate"])
    app.include_router(projects_api.router, tags=["projects"])
    app.include_router(build_api.router, tags=["build"])

    @app.get("/health", response_model=HealthResponse, tags=["meta"])
    def health() -> HealthResponse:
        return HealthResponse(
            codegen_provider=settings.resolve_codegen(),
            builder_provider=settings.builder_provider,
        )

    return app


app = create_app()
