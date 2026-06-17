# Database Schema

The reference build runs on an in-memory repository. For production, set `WI_DATABASE_URL`
(`postgresql+asyncpg://…`) and install the `postgres` extra — the `SqlAlchemyRepository`
activates automatically. The canonical DDL is
[`backend/workflow_intel/persistence/ddl.sql`](../backend/workflow_intel/persistence/ddl.sql).

## Tables

### `analyses`
The aggregate root. The full `AnalysisResult` is stored as `JSONB` (`payload`) with denormalized
summary columns for fast list views and a GIN index for querying inside results.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `varchar(64)` PK | e.g. `wf_ab12…` |
| `created_at` | `timestamptz` | indexed desc |
| `engine` | `varchar(32)` | `deterministic` / `hybrid` / `llm` |
| `model` | `varchar(64)` | LLM model id when applicable |
| `title` | `text` | process summary |
| `step_count`, `bottleneck_count`, `agent_count`, `risk_count` | `int` | summary metrics |
| `source_text` | `text` | original description |
| `payload` | `jsonb` | full result; `GIN (jsonb_path_ops)` |

### `audit_log`
Append-only record of every mutating operation (the API writes one entry per `analyze`).

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigserial` PK | |
| `ts` | `timestamptz` | indexed desc |
| `request_id` | `varchar(64)` | correlates with `X-Request-ID` |
| `action` | `varchar(64)` | e.g. `analyze` |
| `analysis_id` | `varchar(64)` FK | nullable |
| `actor` | `varchar(128)` | verified principal (when auth enabled) |
| `detail` | `jsonb` | structured context |

### `agent_traces`
Normalized per-span observability data (mirrors the OTel export) for analytics/joins.

| Column | Type | Notes |
| --- | --- | --- |
| `span_id` | `varchar(32)` PK | |
| `trace_id` | `varchar(64)` | indexed |
| `parent_span_id` | `varchar(32)` | |
| `analysis_id` | `varchar(64)` FK | `ON DELETE CASCADE` |
| `agent`, `status` | `varchar` | |
| `started_at` | `timestamptz` | |
| `latency_ms`, `cost_usd` | `double precision` | |
| `token_estimate` | `int` | |
| `error` | `text` | |
| `attributes` | `jsonb` | |

## Design notes
- **JSONB-first** keeps the schema stable as the domain model evolves while still enabling
  indexed queries (e.g. risks by category via `payload @> '{"risks":[{"category":"pii"}]}'`).
- **Migrations** — adopt Alembic for production; the DDL here is the v1 baseline.
- **Retention** — `analyses`/`agent_traces` are good candidates for partitioning by month and a
  retention policy; `audit_log` is typically retained longer for compliance.
- **Multi-tenancy** — add a `tenant_id` column + row-level security, or a schema-per-tenant model,
  before going multi-tenant.
