"""API routes for analysis, retrieval, export, diagrams, traces, and meta."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request
from starlette.responses import PlainTextResponse, Response

from workflow_intel import __version__
from workflow_intel.api.schemas import (
    AnalyzeRequest,
    HealthResponse,
    MetaResponse,
    TraceResponse,
)
from workflow_intel.domain.models import AnalysisResult, AnalysisSummary
from workflow_intel.export import to_json, to_yaml
from workflow_intel.knowledge.platforms import PLATFORM_PROFILES
from workflow_intel.knowledge.systems import SYSTEM_CATALOG

router = APIRouter(prefix="/api/v1")


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "-")


@router.post("/analyze", response_model=AnalysisResult, summary="Analyze a workflow description")
async def analyze(req: AnalyzeRequest, request: Request) -> AnalysisResult:
    app = request.app
    coordinator = app.state.coordinator if req.use_llm in (None, True) else app.state.det_coordinator
    result = await coordinator.analyze(req.text)
    await app.state.repository.save(result)
    await app.state.audit.record("analyze", _request_id(request), analysis_id=result.id, engine=result.engine.value)
    return result


@router.get("/analyses", response_model=list[AnalysisSummary], summary="List analyses")
async def list_analyses(request: Request, limit: int = Query(50, ge=1, le=200)) -> list[AnalysisSummary]:
    return await request.app.state.repository.list(limit=limit)


@router.get("/analyses/{analysis_id}", response_model=AnalysisResult, summary="Fetch an analysis")
async def get_analysis(analysis_id: str, request: Request) -> AnalysisResult:
    result = await request.app.state.repository.get(analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result


@router.get("/analyses/{analysis_id}/export", summary="Download the automation spec (JSON/YAML)")
async def export_analysis(
    analysis_id: str, request: Request, format: str = Query("json", pattern="^(json|yaml)$")
) -> Response:
    result = await request.app.state.repository.get(analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if format == "yaml":
        body, media, ext = to_yaml(result), "application/x-yaml", "yaml"
    else:
        body, media, ext = to_json(result), "application/json", "json"
    return Response(
        content=body,
        media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{analysis_id}.{ext}"'},
    )


@router.get("/analyses/{analysis_id}/diagram/{kind}", summary="Get a Mermaid diagram")
async def get_diagram(analysis_id: str, kind: str, request: Request) -> PlainTextResponse:
    result = await request.app.state.repository.get(analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if kind not in result.diagrams:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown diagram '{kind}'. Available: {sorted(result.diagrams)}",
        )
    return PlainTextResponse(result.diagrams[kind], media_type="text/plain")


@router.get("/analyses/{analysis_id}/traces", response_model=TraceResponse, summary="Captured agent traces")
async def get_traces(analysis_id: str, request: Request) -> TraceResponse:
    result = await request.app.state.repository.get(analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return TraceResponse(
        analysis_id=analysis_id,
        trace_id=result.trace[0].trace_id if result.trace else None,
        span_count=len(result.trace),
        total_latency_ms=round(sum(t.latency_ms for t in result.trace), 3),
        total_cost_usd_estimate=round(sum(t.cost_usd_estimate for t in result.trace), 6),
        spans=result.trace,
    )


@router.get("/meta", response_model=MetaResponse, summary="Capabilities & provider status")
async def meta(request: Request) -> MetaResponse:
    app = request.app
    settings = app.state.settings
    provider = app.state.provider
    langgraph_available = False
    try:  # pragma: no cover
        import langgraph  # noqa: F401

        langgraph_available = True
    except Exception:
        langgraph_available = False
    return MetaResponse(
        app_name=settings.app_name,
        version=__version__,
        environment=settings.environment,
        default_engine="hybrid" if provider.available else "deterministic",
        llm_available=provider.available,
        llm_model=settings.llm_model,
        langgraph_available=langgraph_available,
        otel_enabled=settings.otel_enabled,
        supported_systems=sorted(SYSTEM_CATALOG.keys()),
        automation_platforms=[p.value for p in PLATFORM_PROFILES if p.value != "none"],
    )


@router.get("/health", response_model=HealthResponse, summary="Liveness")
async def health() -> HealthResponse:
    return HealthResponse(version=__version__)
