# API Design

Base path: `/api/v1`. OpenAPI/Swagger UI at `/docs`, ReDoc at `/redoc`. All responses are JSON
unless noted. Every response carries `X-Request-ID` and `X-Process-Time-ms` headers.

## Endpoints

### `POST /api/v1/analyze`
Run the multi-agent pipeline on a workflow description.

Request:
```json
{ "text": "Sales emails contracts to Legal...", "title": null, "use_llm": null }
```
- `text` (required, ≥10 chars) — the workflow description.
- `use_llm` — `null` uses the server default; `false` forces the deterministic engine;
  `true` uses the LLM layer if the server has it configured.

Response: `200` with the full `AnalysisResult` (see `export-schema.md` for the shape). `422` on
validation error.

### `GET /api/v1/analyses?limit=50`
List analysis summaries, newest first.

### `GET /api/v1/analyses/{id}`
Fetch the full `AnalysisResult`. `404` if unknown.

### `GET /api/v1/analyses/{id}/export?format=json|yaml`
Download the canonical automation spec. Returns the file with
`Content-Disposition: attachment`. `format` defaults to `json`.

### `GET /api/v1/analyses/{id}/diagram/{kind}`
Return a Mermaid diagram as `text/plain`. `kind` ∈
`workflow | system | agent | data_flow | sequence | integration`. `404` lists valid kinds.

### `GET /api/v1/analyses/{id}/traces`
Return the captured agent spans for the run plus roll-up latency/cost.

```json
{
  "analysis_id": "wf_...",
  "trace_id": "…",
  "span_count": 8,
  "total_latency_ms": 3.2,
  "total_cost_usd_estimate": 0.0,
  "spans": [ { "agent": "workflow_extraction", "status": "ok", "latency_ms": 0.4, ... } ]
}
```

### `GET /api/v1/meta`
Capabilities & provider status: engine default, LLM availability/model, LangGraph availability,
OTel status, recognized systems, and the automation platforms evaluated.

### `GET /api/v1/health`
Liveness probe → `{ "status": "ok", "version": "..." }`.

## Conventions

- **Versioning** — the path carries the major version (`/api/v1`). Breaking changes bump it.
- **Idempotency** — `analyze` creates a new resource each call (returns a fresh `id`); reads are
  side-effect free.
- **Errors** — standard FastAPI error envelope `{ "detail": "..." }` with the appropriate status.
- **Auth** — not enabled in the reference build. In production, terminate auth at the gateway
  (OIDC/JWT) and pass a verified principal; the audit log already records a per-request id and is
  ready to record the actor (see `database.md`).
- **CORS** — configurable via `WI_CORS_ORIGINS`.
- **Rate limiting** — apply at the gateway/ingress; the analyze path is CPU-bound (deterministic)
  or LLM-bound (when enabled) and should be quota'd per tenant.
