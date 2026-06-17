"""Observability Agent — telemetry signals, tooling, dashboards, and SLOs."""

from __future__ import annotations

from workflow_intel.agents.base import Agent
from workflow_intel.agents.state import PipelineState
from workflow_intel.domain.models import Dashboard, ObservabilitySignal, ObservabilitySpec
from workflow_intel.observability.tracing import Span


class ObservabilityAgent(Agent):
    name = "observability"

    async def _execute(self, state: PipelineState, span: Span) -> None:
        signals = [
            ObservabilitySignal(
                name="agent.trace",
                telemetry_type="trace",
                description="End-to-end span per agent invocation (inputs, outputs, decision).",
                otel_instrument="tracer.start_as_current_span",
            ),
            ObservabilitySignal(
                name="workflow.trace",
                telemetry_type="trace",
                description="Root span linking all agent spans for one analysis/run.",
                otel_instrument="tracer.start_as_current_span",
            ),
            ObservabilitySignal(
                name="tool.calls",
                telemetry_type="metric",
                description="Count and outcome of tool/MCP/integration calls.",
                otel_instrument="counter",
                unit="calls",
            ),
            ObservabilitySignal(
                name="agent.latency",
                telemetry_type="metric",
                description="Per-agent and per-tool latency distribution.",
                otel_instrument="histogram",
                unit="ms",
            ),
            ObservabilitySignal(
                name="llm.cost",
                telemetry_type="metric",
                description="Token usage and USD cost per agent and per run.",
                otel_instrument="counter",
                unit="usd",
            ),
            ObservabilitySignal(
                name="agent.failures",
                telemetry_type="metric",
                description="Errors, timeouts, schema-validation failures, guardrail blocks.",
                otel_instrument="counter",
                unit="errors",
            ),
            ObservabilitySignal(
                name="agent.recovery",
                telemetry_type="metric",
                description="Retries, fallbacks, and compensating-transaction executions.",
                otel_instrument="counter",
                unit="events",
            ),
            ObservabilitySignal(
                name="hitl.escalations",
                telemetry_type="metric",
                description="Human-in-the-loop escalations and their resolution outcome.",
                otel_instrument="counter",
                unit="events",
            ),
        ]
        tools = [
            {"tool": "OpenTelemetry", "purpose": "Vendor-neutral trace/metric/log instrumentation and export."},
            {"tool": "LangSmith", "purpose": "LLM/agent trace inspection, prompt/version diffing, dataset evals."},
            {"tool": "Arize", "purpose": "Production ML/LLM observability, drift, and quality monitoring."},
            {"tool": "Phoenix", "purpose": "Open-source LLM tracing & evaluation during development."},
            {"tool": "Grafana", "purpose": "Operational dashboards and alerting over the metric/trace backend."},
        ]
        dashboards = [
            Dashboard(
                name="Agent Performance",
                tool="Grafana / LangSmith",
                panels=[
                    "Latency p50/p95/p99 by agent",
                    "Throughput",
                    "Error rate",
                    "Token & cost by agent",
                    "Tool-call success rate",
                ],
            ),
            Dashboard(
                name="Workflow Health",
                tool="Grafana",
                panels=[
                    "Runs/min",
                    "End-to-end duration",
                    "Stage funnel & drop-off",
                    "Dead-letter queue depth",
                    "Recovery/retry rate",
                ],
            ),
            Dashboard(
                name="Cost & Tokens",
                tool="Grafana",
                panels=["USD/run", "Tokens/run by agent", "Cache hit rate", "Cost anomaly alerts"],
            ),
            Dashboard(
                name="Governance & Escalation",
                tool="LangSmith / Grafana",
                panels=[
                    "HITL escalation rate",
                    "Escalation precision/recall",
                    "Guardrail blocks",
                    "Approval SLA breaches",
                ],
            ),
            Dashboard(
                name="Quality & Drift",
                tool="Arize / Phoenix",
                panels=["Eval scores over time", "Groundedness/faithfulness", "Routing accuracy", "Input/output drift"],
            ),
        ]
        slos = [
            {"objective": "Analysis availability", "target": "99.9% monthly"},
            {"objective": "End-to-end p95 latency", "target": "< 8s (deterministic) / < 30s (LLM)"},
            {"objective": "Agent error rate", "target": "< 1% of runs"},
            {"objective": "Escalation precision", "target": "> 0.85"},
            {"objective": "Cost per analysis", "target": "within budget envelope, alert at 1.5×"},
        ]
        state.observability = ObservabilitySpec(signals=signals, tools=tools, dashboards=dashboards, slos=slos)
        span.set(signals=len(signals), dashboards=len(dashboards))
