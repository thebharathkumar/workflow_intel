"""FastAPI application factory and wiring."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from workflow_intel import __version__
from workflow_intel.agents.coordinator import Coordinator
from workflow_intel.api.middleware import RequestContextMiddleware
from workflow_intel.api.routes import router
from workflow_intel.config import get_settings
from workflow_intel.llm.provider import NullProvider, get_provider
from workflow_intel.observability.tracing import configure_otel
from workflow_intel.persistence.repository import AuditLogger, get_repository


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.otel_enabled:
        configure_otel(settings.service_name, settings.otel_endpoint)

    provider = get_provider(settings)
    app.state.settings = settings
    app.state.provider = provider
    app.state.coordinator = Coordinator(settings, provider)
    app.state.det_coordinator = Coordinator(settings, NullProvider())
    app.state.repository = get_repository(settings)
    app.state.audit = AuditLogger()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Workflow Intel API",
        version=__version__,
        description="AI-powered business workflow analysis, automation architecture, and agentic systems design.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextMiddleware)
    app.include_router(router)

    @app.get("/", include_in_schema=False)
    async def root() -> dict:
        return {
            "name": settings.app_name,
            "version": __version__,
            "docs": "/docs",
            "api": "/api/v1",
        }

    return app


app = create_app()
