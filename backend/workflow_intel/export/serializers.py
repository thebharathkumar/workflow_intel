"""Build and serialize the canonical Workflow Intel automation specification.

The spec is a stable, self-describing document covering workflow, agents, systems, integrations,
governance, risks, observability, evaluation, and roll-up metrics — the downloadable artifact a
team would hand to engineering to implement.
"""

from __future__ import annotations

import json

import yaml

from workflow_intel.domain.models import AnalysisResult

SPEC_VERSION = "1.0"


def to_spec(result: AnalysisResult) -> dict:
    """Project an :class:`AnalysisResult` into the canonical export schema."""
    data = result.model_dump(mode="json")
    annual_hours = round(sum(b.annual_hours_saved for b in result.bottlenecks), 1)
    return {
        "workflow_intel_spec_version": SPEC_VERSION,
        "metadata": {
            "id": result.id,
            "created_at": data["created_at"],
            "engine": result.engine.value,
            "model": result.model,
            "source_text": result.source_text,
        },
        "process": data["process_report"],
        "workflow": {
            "steps": data["workflow"]["steps"],
            "actors": data["workflow"]["actors"],
            "systems": data["workflow"]["systems"],
            "handoffs": data["workflow"]["handoffs"],
            "graph": result.workflow.to_json_graph(),
        },
        "bottlenecks": data["bottlenecks"],
        "automation": data["automations"],
        "agents": data["agents"],
        "systems": data["workflow"]["systems"],
        "integrations": data["integrations"],
        "governance": data["governance"],
        "risks": data["risks"],
        "observability": data["observability"],
        "evaluation": data["evaluation"],
        "diagrams": data["diagrams"],
        "metrics": {
            "total_steps": len(result.workflow.steps),
            "total_actors": len(result.workflow.actors),
            "total_systems": len(result.workflow.systems),
            "bottlenecks": len(result.bottlenecks),
            "agents_designed": len(result.agents),
            "integrations": len(result.integrations),
            "risks": len(result.risks),
            "prohibited_steps": sum(1 for g in result.governance if g.classification.value == "prohibited_automation"),
            "estimated_annual_hours_saved": annual_hours,
            "pipeline_cost_usd_estimate": round(sum(t.cost_usd_estimate for t in result.trace), 6),
            "pipeline_latency_ms": round(sum(t.latency_ms for t in result.trace), 3),
        },
    }


def to_json(result: AnalysisResult, *, spec: bool = True, indent: int = 2) -> str:
    payload = to_spec(result) if spec else result.model_dump(mode="json")
    return json.dumps(payload, indent=indent, ensure_ascii=False)


def to_yaml(result: AnalysisResult, *, spec: bool = True) -> str:
    payload = to_spec(result) if spec else result.model_dump(mode="json")
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=100)
