-- Workflow Intel — PostgreSQL schema
-- The SqlAlchemyRepository creates `analyses` automatically; this file is the canonical,
-- production-grade DDL (indexes, audit log, and a normalized trace table for analytics).

CREATE TABLE IF NOT EXISTS analyses (
    id               VARCHAR(64) PRIMARY KEY,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    engine           VARCHAR(32) NOT NULL,
    model            VARCHAR(64),
    title            TEXT NOT NULL,
    step_count       INTEGER NOT NULL DEFAULT 0,
    bottleneck_count INTEGER NOT NULL DEFAULT 0,
    agent_count      INTEGER NOT NULL DEFAULT 0,
    risk_count       INTEGER NOT NULL DEFAULT 0,
    source_text      TEXT NOT NULL,
    payload          JSONB NOT NULL          -- full AnalysisResult
);

CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_engine     ON analyses (engine);
-- GIN index enables querying inside the stored result, e.g. risks by category.
CREATE INDEX IF NOT EXISTS idx_analyses_payload    ON analyses USING GIN (payload jsonb_path_ops);

-- Append-only audit trail for every mutating operation.
CREATE TABLE IF NOT EXISTS audit_log (
    id          BIGSERIAL PRIMARY KEY,
    ts          TIMESTAMPTZ NOT NULL DEFAULT now(),
    request_id  VARCHAR(64) NOT NULL,
    action      VARCHAR(64) NOT NULL,
    analysis_id VARCHAR(64) REFERENCES analyses (id) ON DELETE SET NULL,
    actor       VARCHAR(128),
    detail      JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_audit_ts          ON audit_log (ts DESC);
CREATE INDEX IF NOT EXISTS idx_audit_analysis_id ON audit_log (analysis_id);

-- Normalized agent traces for observability analytics (mirrors the OTel export).
CREATE TABLE IF NOT EXISTS agent_traces (
    span_id        VARCHAR(32) PRIMARY KEY,
    trace_id       VARCHAR(64) NOT NULL,
    parent_span_id VARCHAR(32),
    analysis_id    VARCHAR(64) REFERENCES analyses (id) ON DELETE CASCADE,
    agent          VARCHAR(64) NOT NULL,
    status         VARCHAR(16) NOT NULL,
    started_at     TIMESTAMPTZ NOT NULL,
    latency_ms     DOUBLE PRECISION NOT NULL DEFAULT 0,
    token_estimate INTEGER NOT NULL DEFAULT 0,
    cost_usd       DOUBLE PRECISION NOT NULL DEFAULT 0,
    error          TEXT,
    attributes     JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_traces_trace_id    ON agent_traces (trace_id);
CREATE INDEX IF NOT EXISTS idx_traces_analysis_id ON agent_traces (analysis_id);
CREATE INDEX IF NOT EXISTS idx_traces_agent       ON agent_traces (agent);
