# Export Schema

`GET /analyses/{id}/export?format=json|yaml` returns the canonical **Workflow Intel automation
spec** — a stable, self-describing document built by `export/serializers.py` (`to_spec`). It is the
artifact handed to engineering to implement the automation.

## Top-level shape
```yaml
workflow_intel_spec_version: "1.0"
metadata:        { id, created_at, engine, model, source_text }
process:         { summary, business_objective, participants, systems, inputs, outputs,
                   dependencies, risk_areas }
workflow:
  steps:         [ { id, name, type, actor, systems, inputs, outputs, order, is_manual,
                     is_external_comm, is_repetitive, touches_pii, financial_impact, irreversible } ]
  actors:        [ { name, type, role } ]
  systems:       [ { name, category, vendor } ]
  handoffs:      [ { from_step, to_step, from_actor, to_actor, mechanism } ]
  graph:         { graph: { directed, nodes, edges } }        # JSON Graph Format
bottlenecks:     [ { type, title, description, step_ids, impact_score, complexity_score,
                     confidence_score, estimated_roi, annual_hours_saved, ai_capability,
                     recommendation } ]
automation:      [ { step_id, step_name, automation_type, suggested_platform,
                     alternative_platforms, reasoning, confidence_score, prerequisites } ]
agents:          [ { name, purpose, responsibilities, inputs, outputs, tools,
                     memory_requirements, escalation_rules, hitl_rules, evaluation_metrics,
                     failure_modes, recovery_strategy, guardrails } ]
systems:         [ { name, category, vendor } ]
integrations:    [ { system, category, vendor, direction, api_requirements, auth_methods,
                     event_triggers, webhooks, data_objects, mcp_opportunity } ]
governance:      [ { step_id, step_name, classification, rationale, controls } ]
risks:           [ { category, title, description, severity, likelihood, risk_score,
                     mitigation, owner } ]
observability:   { signals, tools, dashboards, slos }
evaluation:      [ { name, target, metric, kpi_target, method, dataset, cadence } ]
diagrams:        { workflow, system, agent, data_flow, sequence, integration }   # Mermaid
metrics:
  total_steps: 5
  total_actors: 3
  total_systems: 3
  bottlenecks: 5
  agents_designed: 1
  integrations: 3
  risks: 3
  prohibited_steps: 0
  estimated_annual_hours_saved: 826.0
  pipeline_cost_usd_estimate: 0.0
  pipeline_latency_ms: 3.2
```

## Enumerations
- `automation_type`: `human | agent | workflow_engine | integration | rpa`
- `suggested_platform`: `n8n | workato | make | zapier | langgraph | temporal | airflow | none`
- `classification`: `safe_for_full_automation | human_approval_required | human_review_recommended | prohibited_automation`
- `risk.category`: `hallucination | data_leakage | compliance | pii | financial | operational`
- `severity`: `low | medium | high | critical`; `likelihood`: `rare | unlikely | possible | likely | almost_certain`

## Guarantees
- **Round-trippable** — `AnalysisResult.model_validate(model_dump())` is lossless (covered by tests).
- **Versioned** — `workflow_intel_spec_version` lets consumers gate on schema changes.
- **Self-contained** — every reference (agent→step, governance→step, edge→node) resolves within
  the document.
- **Machine-actionable** — `workflow.graph` is JSON Graph Format; `diagrams` are ready-to-render
  Mermaid; `automation`/`integrations` carry everything a generator needs to scaffold the build.
