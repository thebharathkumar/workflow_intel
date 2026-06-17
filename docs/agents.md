# Agent Design

The pipeline is eight specialist agents plus a coordinator. Each is an async, traced unit
(`agents/base.py`) sharing one `PipelineState`. Every agent has a deterministic implementation and
(at the extraction stage) an optional LLM path; all are instrumented identically.

## Pipeline agents

| Agent | Module | Input | Output | Key logic |
| --- | --- | --- | --- | --- |
| **Workflow Extraction** | `extraction.py` | raw text | `WorkflowGraph` | Lexicon + verb rules → typed steps, actors, systems, handoffs, feature flags. LLM path: NL→structure via structured outputs, then the *same* flag computation. |
| **Process Intelligence** | `intelligence.py` | graph | report + `Bottleneck[]` | Builds the intelligence report; detects human/system/AI-candidate bottlenecks with impact/complexity/confidence/ROI scoring. |
| **Automation Architect** | `automation.py` | graph | `AutomationRecommendation[]` + `AgentDesign[]` | Maps each step to an automation type, picks a platform with reasoning, and designs agents for agentic steps. |
| **Governance** | `governance.py` | graph | `GovernanceClassification[]` + `RiskItem[]` | Four-tier classification matrix; six-category risk register with severity × likelihood. |
| **Integration** | `integration.py` | systems | `Integration[]` | Grounds each system in the catalog: API, auth, events, webhooks, MCP. |
| **Observability** | `observability_agent.py` | result-so-far | `ObservabilitySpec` | Telemetry signals, tooling, dashboards, SLOs. |
| **Evaluation** | `evaluation.py` | result-so-far | `EvaluationSpec[]` | Workflow/agent/routing/tool/escalation/STP evals with KPIs. |
| **Diagram Generation** | `diagram.py` | full result | `diagrams{}` | Five Mermaid diagrams + the workflow diagram. |

The **Coordinator** (`coordinator.py`) runs extraction → `[automation, integration]` fan-out →
governance → `[observability, evaluation]` fan-out → diagrams, then assembles the
`AnalysisResult`. The `graph/langgraph_flow.py` adapter expresses the same DAG as a LangGraph
`StateGraph`.

## Generated agent specifications

For every step the Automation Architect classifies as agentic, it emits a full `AgentDesign`
covering the dimensions the brief requires:

- **Name** — e.g. *Contract Review Agent*, *Ticket Triage Agent* (derived from the step's AI capability).
- **Responsibilities** — ingest, apply capability against policy/templates, produce a structured
  recommendation with citations + confidence, escalate.
- **Inputs / Outputs** — upstream artifacts and policy context → recommendation + confidence + rationale.
- **Tools** — system MCP tools for the step's systems + retrieval over policy/templates.
- **Memory requirements** — short-term (case window), long-term (vector store of prior decisions
  & policies), episodic (audit log).
- **Escalation rules** — confidence threshold, anomaly/out-of-policy, mandatory escalation for
  material decisions.
- **HITL rules** — human approval before irreversible/external actions; reviewer accept/edit/reject
  feeds back as training signal.
- **Evaluation metrics** — decision accuracy vs. gold, escalation precision/recall, groundedness,
  time-to-decision.
- **Failure modes** — hallucination, misclassification, tool timeout/partial write, prompt injection.
- **Recovery strategy** — idempotent retries with backoff → human queue; compensating transactions
  for side effects.
- **Guardrails** — structured-output schema constraint, allow-listed tools, PII/secret redaction.

These map directly to the multi-agent and human-in-the-loop sections of the brief, and are the
artifact a team would hand to engineering to implement the agent.
