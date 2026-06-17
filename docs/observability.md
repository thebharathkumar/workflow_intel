# Observability Framework

Observability is built into the runtime, not just recommended. Two things ship:

1. **Live instrumentation** — every agent runs inside `trace_agent` (`observability/tracing.py`),
   which records a span (agent, status, latency, token/cost estimate, attributes) to an in-process
   `SpanRecorder` **and** to OpenTelemetry when an SDK/exporter is configured. The recorder's
   spans are attached to each result and returned by `GET /analyses/{id}/traces`, so traces are
   demonstrable with zero external infrastructure.
2. **A generated observability spec** — the Observability Agent emits the telemetry signals,
   tooling, dashboards, and SLOs a team should stand up for the *recommended* automation.

## Captured signals (per run, live)
`trace_id`, `span_id`, `parent_span_id`, `agent`, `status`, `started_at`, `latency_ms`,
`token_estimate`, `cost_usd_estimate`, `error`, and arbitrary `attributes` (e.g. step counts,
engine, agents designed).

## Recommended signals (in the spec)
| Signal | Type | OTel instrument |
| --- | --- | --- |
| `agent.trace` / `workflow.trace` | trace | span |
| `tool.calls` | metric (counter) | calls |
| `agent.latency` | metric (histogram) | ms |
| `llm.cost` | metric (counter) | usd |
| `agent.failures` | metric (counter) | errors |
| `agent.recovery` | metric (counter) | events |
| `hitl.escalations` | metric (counter) | events |

## Tooling
- **OpenTelemetry** — vendor-neutral trace/metric/log instrumentation & export (the spine).
- **LangSmith** — LLM/agent trace inspection, prompt/version diffing, dataset evals.
- **Arize** — production LLM observability, drift & quality monitoring.
- **Phoenix** — open-source LLM tracing & evaluation in development.
- **Grafana** — operational dashboards & alerting over the metric/trace backend.

## Dashboards (generated)
Agent Performance · Workflow Health · Cost & Tokens · Governance & Escalation · Quality & Drift —
each with concrete panels (latency percentiles, STP funnel, cost/run, escalation precision,
groundedness, drift).

## SLOs (generated)
Availability 99.9% · p95 latency < 8s (deterministic) / < 30s (LLM) · agent error rate < 1% ·
escalation precision > 0.85 · cost-per-analysis within budget with a 1.5× alert.

## Wiring OTel
Set `WI_OTEL_ENABLED=true` and `WI_OTEL_ENDPOINT=<collector>`; install the `otel` extra. The
`docker-compose.yml` includes an OpenTelemetry Collector you can point Grafana/Tempo/Phoenix at.
