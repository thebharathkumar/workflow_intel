"""Request/response DTOs for the API (kept distinct from domain models)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from workflow_intel.domain.models import AgentTrace


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=10, description="Plain-English workflow description.")
    title: str | None = Field(default=None, description="Optional label for the analysis.")
    use_llm: bool | None = Field(
        default=None,
        description="Override the LLM layer for this request. None → server default; "
        "False → force deterministic; True → use LLM if the server has it configured.",
    )


class MetaResponse(BaseModel):
    app_name: str
    version: str
    environment: str
    default_engine: str
    llm_available: bool
    llm_model: str
    langgraph_available: bool
    otel_enabled: bool
    supported_systems: list[str]
    automation_platforms: list[str]


class TraceResponse(BaseModel):
    analysis_id: str
    trace_id: str | None
    span_count: int
    total_latency_ms: float
    total_cost_usd_estimate: float
    spans: list[AgentTrace]


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
