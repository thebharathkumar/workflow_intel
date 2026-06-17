# Future Roadmap

The current platform analyzes a description into a governed, observable automation blueprint. The
roadmap turns blueprints into running, learning systems.

## Near term (next quarter)
- **Process library + retrieval** — vector store of prior analyses and reference processes; the
  Extraction and Automation agents retrieve similar workflows to ground recommendations (RAG).
- **Editable canvas** — promote the React Flow canvas from read-only to an editor; edits re-run the
  affected agents and re-export the spec (round-trip authoring).
- **Auth & multi-tenancy** — OIDC/JWT, per-tenant isolation (RLS), workspaces, and shareable links.
- **LLM-as-judge evals in CI** — wire the generated eval suite to a runnable harness with golden
  datasets and dashboards, gating releases.
- **Richer extraction** — coreference and multi-sentence step merging; confidence per extracted
  element; user correction loop that becomes training data.

## Mid term
- **Blueprint → scaffolding** — generate starter artifacts for the recommended platform: n8n/Make
  workflow JSON, a Temporal workflow skeleton, or a runnable LangGraph agent stub with the designed
  tools, memory, and HITL checkpoints wired in.
- **Simulation / what-if** — Monte-Carlo over step latencies and volumes to quantify cycle-time and
  ROI before building; compare "before vs. after automation" scenarios.
- **Live MCP catalog** — connect to real MCP servers for the recommended systems and validate the
  integration plan against live schemas.
- **Cost & ROI modeling** — replace heuristic hours-saved with a calibrated model fed by actual
  cycle-time telemetry.

## Long term
- **Closed-loop execution** — deploy approved automations to the chosen engine, then feed
  production traces/evals back to refine the blueprint (continuous improvement).
- **Org-wide process graph** — stitch many analyzed workflows into a single dependency graph to
  surface cross-process bottlenecks and shared-integration opportunities.
- **Policy-as-code governance** — express governance tiers and controls as versioned policy
  (OPA/Rego) enforced at deploy time, with attestation.
- **Agent marketplace** — reusable, evaluated agent templates (Contract Review, Ticket Triage, …)
  with published eval scorecards.

## Guiding principles
- Keep the deterministic core authoritative and explainable; the LLM and execution layers are
  always additive.
- Every new capability ships with its evals and its telemetry — observability and evaluation are
  features, not afterthoughts.
- Governance stays first-class: nothing becomes "executable" without its classification and controls.
