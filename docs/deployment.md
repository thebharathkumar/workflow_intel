# Production Deployment Plan

## Topology
```
        ┌────────────┐      ┌──────────────────────┐
Users → │  CDN/WAF   │ ───► │  Ingress / API GW     │ (TLS, OIDC/JWT, rate limit, WAF)
        └────────────┘      └─────────┬────────────┘
                          ┌───────────┴───────────┐
                          ▼                        ▼
                 ┌─────────────────┐      ┌─────────────────┐
                 │ frontend (nginx)│      │ backend (uvicorn│
                 │  static SPA     │      │  + gunicorn)    │  (HPA: N replicas)
                 └─────────────────┘      └───────┬─────────┘
                                                  │
              ┌────────────────┬──────────────────┼───────────────────┐
              ▼                ▼                  ▼                   ▼
        ┌───────────┐   ┌────────────┐    ┌──────────────┐    ┌──────────────┐
        │ PostgreSQL│   │ OTel Coll. │    │ Anthropic API│    │ Secrets mgr  │
        │ (managed) │   │→Tempo/Graf │    │ (optional)   │    │ (KMS/Vault)  │
        └───────────┘   └────────────┘    └──────────────┘    └──────────────┘
```

## Build & run
- **Backend image** — `docker/Dockerfile.backend` (Python 3.11-slim, non-root, `gunicorn` with
  `uvicorn.workers.UvicornWorker`). Healthcheck hits `/api/v1/health`.
- **Frontend image** — `docker/Dockerfile.frontend` (multi-stage: `npm run build` → nginx serving
  static assets, proxying `/api` to the backend).
- **Local/full stack** — `docker compose up --build` brings up backend, frontend, Postgres, and an
  OTel Collector.

## Configuration (env)
| Var | Purpose |
| --- | --- |
| `WI_ENVIRONMENT` | `production` |
| `WI_DATABASE_URL` | `postgresql+asyncpg://…` (enables SQL repo) |
| `WI_CORS_ORIGINS` | allowed origins |
| `WI_LLM_ENABLED`, `ANTHROPIC_API_KEY`, `WI_LLM_MODEL` | optional LLM layer (`claude-opus-4-8`) |
| `WI_USE_LANGGRAPH` | run the true LangGraph StateGraph |
| `WI_OTEL_ENABLED`, `WI_OTEL_ENDPOINT` | OpenTelemetry export |

Secrets come from a secret manager (never baked into images). The API key, if used, is mounted at
runtime.

## Scaling & reliability
- **Stateless backend** — scale horizontally behind the gateway; target CPU/RPS with an HPA. The
  deterministic path is CPU-bound and fast; the LLM path is I/O-bound — size separate pools or a
  queue if LLM analyses are heavy.
- **Database** — managed Postgres with read replicas for list/analytics; PITR backups; monthly
  partitioning + retention on `analyses`/`agent_traces`.
- **Resilience** — liveness/readiness probes, graceful shutdown, request timeouts, and (for the LLM
  path) the SDK's built-in retries plus a circuit breaker.
- **Caching** — when the LLM layer is on, prompt caching keeps the frozen system prompt cached;
  results are persisted so repeat reads never re-run the pipeline.

## Security
- TLS everywhere; OIDC/JWT at the gateway; the audit log records request id + verified actor.
- Least-privilege DB role; row-level security if multi-tenant.
- DLP/PII redaction on logs; secrets via KMS/Vault; SBOM + image scanning in CI.
- Network policy: backend egress restricted to Postgres, the OTel collector, and (if enabled) the
  Anthropic API.

## CI/CD
1. Lint (`ruff`), type-check (`mypy`, `tsc`), test (`pytest`, vite build).
2. Run the eval suite (`docs/evaluation.md`) as a release gate.
3. Build & scan images; push to registry.
4. Deploy via GitOps (Argo/Flux) or Helm; run DB migrations (Alembic) as a pre-deploy job.
5. Progressive rollout (canary) watched by the Agent Performance & Quality dashboards; auto-roll
   back on SLO breach.

## Runbooks (starting set)
- LLM provider outage → `WI_LLM_ENABLED=false` falls the system back to the deterministic engine
  with no downtime.
- Cost spike → Cost & Tokens dashboard alert at 1.5× budget; throttle per-tenant quota.
- Eval regression → block release; pin to the prior agent version.
