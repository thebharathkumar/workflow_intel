"""Tracing for the agent pipeline.

Every agent runs inside :func:`trace_agent`, which times the call, captures status/cost, and
records an :class:`~workflow_intel.domain.models.AgentTrace`. Traces are written to an in-process
:class:`SpanRecorder` (always) and to OpenTelemetry (when an SDK/exporter is configured). The
recorder's spans are attached to the result and surfaced via ``GET /analyses/{id}/traces`` — so
the observability story is verifiable with zero external infrastructure.
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import Any
from uuid import uuid4

from workflow_intel.domain.models import AgentTrace

# Anthropic claude-opus-4-8 pricing (USD per 1M tokens).
_INPUT_PER_MTOK = 5.0
_OUTPUT_PER_MTOK = 25.0

# Optional OpenTelemetry bridge — degrades to a no-op when the SDK is absent.
try:  # pragma: no cover - depends on optional dependency
    from opentelemetry import trace as _otel_trace

    _OTEL_AVAILABLE = True
except Exception:  # pragma: no cover
    _otel_trace = None  # type: ignore[assignment]
    _OTEL_AVAILABLE = False


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """Estimate USD cost for a claude-opus-4-8 call."""
    return round(
        input_tokens / 1_000_000 * _INPUT_PER_MTOK + output_tokens / 1_000_000 * _OUTPUT_PER_MTOK,
        6,
    )


def configure_otel(service_name: str, endpoint: str | None) -> bool:
    """Best-effort OTel SDK configuration. Returns True if a tracer provider was set up."""
    if not _OTEL_AVAILABLE:  # pragma: no cover
        return False
    try:  # pragma: no cover - exercised only with the otel extra installed
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
        if endpoint:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

            provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
        _otel_trace.set_tracer_provider(provider)
        return True
    except Exception:
        return False


class Span:
    """Mutable handle an agent uses to annotate its span with cost and attributes."""

    def __init__(self, agent: str, trace_id: str, parent_span_id: str | None) -> None:
        self.agent = agent
        self.trace_id = trace_id
        self.span_id = uuid4().hex[:16]
        self.parent_span_id = parent_span_id
        self.input_tokens = 0
        self.output_tokens = 0
        self.attributes: dict[str, Any] = {}
        self.status = "ok"
        self.error: str | None = None

    def set_tokens(self, input_tokens: int, output_tokens: int) -> None:
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens

    def set(self, **attributes: Any) -> None:
        self.attributes.update(attributes)


class SpanRecorder:
    """Collects spans for a single pipeline run under one trace id."""

    def __init__(self, trace_id: str | None = None) -> None:
        self.trace_id = trace_id or uuid4().hex
        self.traces: list[AgentTrace] = []

    def record(self, span: Span, latency_ms: float) -> None:
        self.traces.append(
            AgentTrace(
                trace_id=span.trace_id,
                span_id=span.span_id,
                parent_span_id=span.parent_span_id,
                agent=span.agent,
                status=span.status,
                latency_ms=round(latency_ms, 3),
                token_estimate=span.input_tokens + span.output_tokens,
                cost_usd_estimate=estimate_cost(span.input_tokens, span.output_tokens),
                error=span.error,
                attributes=span.attributes,
            )
        )

    def total_cost(self) -> float:
        return round(sum(t.cost_usd_estimate for t in self.traces), 6)

    def total_latency_ms(self) -> float:
        return round(sum(t.latency_ms for t in self.traces), 3)


@asynccontextmanager
async def trace_agent(recorder: SpanRecorder, agent: str, parent_span_id: str | None = None):
    """Async context manager wrapping one agent execution in a recorded span."""
    span = Span(agent=agent, trace_id=recorder.trace_id, parent_span_id=parent_span_id)
    otel_cm = None
    otel_span = None
    if _OTEL_AVAILABLE:  # pragma: no cover
        tracer = _otel_trace.get_tracer("workflow_intel")
        otel_cm = tracer.start_as_current_span(f"agent.{agent}")
        otel_span = otel_cm.__enter__()
    start = time.perf_counter()
    try:
        yield span
    except Exception as exc:  # record failure, then re-raise
        span.status = "error"
        span.error = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        latency_ms = (time.perf_counter() - start) * 1000.0
        recorder.record(span, latency_ms)
        if otel_span is not None:  # pragma: no cover
            for key, value in span.attributes.items():
                try:
                    otel_span.set_attribute(f"wi.{key}", value)
                except Exception:
                    pass
            otel_span.set_attribute("wi.latency_ms", latency_ms)
            otel_span.set_attribute("wi.cost_usd", estimate_cost(span.input_tokens, span.output_tokens))
            otel_cm.__exit__(None, None, None)  # type: ignore[union-attr]
