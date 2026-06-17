# Workflow Intel

**An AI-powered Business Workflow Analyzer, Automation Architect, and Agentic Systems Design Platform.**

Workflow Intel transforms ambiguous, plain-English business process descriptions into
structured, observable, governable, AI-enabled automation blueprints.

> A business stakeholder types: *"Sales emails contracts to Legal. Legal reviews and sends
> comments back. Sales updates Salesforce. Finance receives a Slack notification. Contracts
> are stored in SharePoint."*
>
> Workflow Intel returns a process-intelligence report, a workflow DAG, bottleneck analysis,
> an automation blueprint, an agent architecture, an enterprise integration plan, a governance
> & AI-risk assessment, an observability framework, an evaluation framework, architecture
> diagrams, and a downloadable JSON/YAML automation specification.

This is **not** a thin LLM wrapper. It is a multi-agent analysis pipeline with a deterministic
core, an optional LLM enhancement layer, first-class observability (every agent step is traced),
governance classification, and an evaluation framework — designed to read like something a
Solutions Architect or AI Transformation Consultant would actually ship.

---

## Why it's architected the way it is

| Decision | Rationale |
| --- | --- |
| **Deterministic core + optional LLM layer** | The analysis engine produces a full blueprint with *zero* external dependencies or API keys, so it is runnable, testable, and CI-friendly. When an Anthropic API key is present, agents transparently upgrade to LLM-backed extraction/reasoning (`claude-opus-4-8`, structured outputs). |
| **Orchestration policy separated from agent logic** | Agents are plain async callables. A pure-Python `Coordinator` is the source of truth for the DAG; a `LangGraph` adapter (`graph/langgraph_flow.py`) builds an equivalent `StateGraph` when LangGraph is installed. The pipeline is therefore "implemented using LangGraph" without making LangGraph a hard runtime dependency. |
| **Observability is built in, not bolted on** | Every agent runs inside a traced span (OpenTelemetry when configured, an in-memory recorder otherwise). Captured traces — agent name, latency, token/cost estimates, status — are returned by the API, so observability is demonstrable end-to-end. |
| **Repository pattern for persistence** | Default `InMemoryRepository` keeps the app runnable; a SQLAlchemy/PostgreSQL implementation and DDL ship alongside for production. |

---

## Repository structure

```
workflow_intel/
├── README.md                      # this file
├── ARCHITECTURE.md                # full architecture deep-dive
├── Makefile                       # dev workflows
├── docker-compose.yml             # backend + frontend + postgres + otel-collector
├── docs/
│   ├── api.md                     # REST API reference
│   ├── database.md                # schema + DDL
│   ├── agents.md                  # agent design specs
│   ├── governance.md              # governance framework
│   ├── observability.md           # observability framework
│   ├── evaluation.md              # evaluation framework
│   ├── diagrams.md                # system / data-flow / sequence Mermaid
│   ├── export-schema.md           # JSON/YAML automation-spec schema
│   ├── deployment.md              # production deployment plan
│   └── roadmap.md                 # future roadmap
├── backend/
│   ├── pyproject.toml
│   ├── workflow_intel/
│   │   ├── config.py              # typed settings
│   │   ├── domain/                # Pydantic domain model (the contract)
│   │   │   ├── enums.py
│   │   │   ├── models.py
│   │   │   └── schema.py
│   │   ├── knowledge/             # enterprise systems + automation-platform catalogs
│   │   ├── analysis/              # deterministic NLP heuristics
│   │   ├── llm/                   # provider abstraction (Anthropic + null)
│   │   ├── observability/         # tracing + metrics
│   │   ├── agents/                # the 8 specialist agents + coordinator
│   │   ├── graph/                 # optional LangGraph StateGraph adapter
│   │   ├── persistence/           # repository protocol + in-memory + SQL
│   │   ├── export/                # JSON/YAML serializers
│   │   ├── api/                   # FastAPI app, routes, middleware
│   │   └── cli.py                 # `python -m workflow_intel.cli analyze "..."`
│   └── tests/
└── frontend/                      # React + TypeScript + Tailwind + React Flow
    └── src/
        ├── pages/                 # Landing, Analyzer, Results, Canvas, Governance, Observability
        ├── components/
        └── lib/                   # API client + types
```

---

## Quick start

### Backend (no API key required)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn workflow_intel.api.app:app --reload --port 8000
# → http://localhost:8000/docs
```

Analyze from the CLI:

```bash
python -m workflow_intel.cli analyze \
  "Sales emails contracts to Legal. Legal reviews and sends comments back. \
   Sales updates Salesforce. Finance receives a Slack notification. \
   Contracts are stored in SharePoint." --format yaml
```

Enable the LLM layer (optional):

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export WI_LLM_ENABLED=true        # agents now use claude-opus-4-8 with structured outputs
```

### Frontend

```bash
cd frontend
npm install
npm run dev          # → http://localhost:5173 (proxies /api to :8000)
```

### Everything, containerized

```bash
docker compose up --build
```

---

## The twelve outputs

1. **Process Intelligence Report** — summary, objective, participants, systems, inputs, outputs, dependencies, risk areas
2. **Workflow Graph** — DAG with steps/actors/systems/decisions/approvals; Mermaid, React Flow, and JSON renderers
3. **Bottleneck Detection** — human / system / AI-candidate, each scored for impact, complexity, confidence, ROI
4. **Automation Blueprint** — per-step automation type + suggested platform (n8n / Workato / Make / Zapier / LangGraph / Temporal / Airflow) with reasoning
5. **Agent Architecture** — designed agents with responsibilities, I/O, tools, memory, escalation, HITL, eval metrics, failure modes, recovery
6. **Enterprise Integration Layer** — systems, API requirements, auth, events, webhooks, MCP opportunities
7. **Governance Analysis** — every step classified (full automation / human approval / human review / prohibited) with rationale
8. **AI Risk Assessment** — hallucination / data-leakage / compliance / PII / financial / operational, each with severity, likelihood, mitigation
9. **Observability Framework** — traces, metrics, dashboards (OpenTelemetry / LangSmith / Arize / Phoenix / Grafana)
10. **Evaluation Framework** — workflow / agent / routing / tool-selection / escalation / success-rate evals with measurable KPIs
11. **Architecture Diagrams** — system, agent, data-flow, sequence, integration (Mermaid)
12. **Automation Specification Export** — downloadable JSON & YAML covering workflow, agents, systems, integrations, governance, risks, metrics

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the full design and [`docs/`](./docs) for per-domain detail.
