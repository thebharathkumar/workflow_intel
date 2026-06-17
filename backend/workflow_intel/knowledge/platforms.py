"""Automation-platform profiles and a platform-selection heuristic.

Given a recommended automation *type* and a step's features, ``recommend_platform`` returns the
best-fit platform, ranked alternatives, and a written rationale — the kind of justified
recommendation a solutions architect would defend in a review.
"""

from __future__ import annotations

from typing import Any

from workflow_intel.domain.enums import AutomationType, Platform

PLATFORM_PROFILES: dict[Platform, dict[str, Any]] = {
    Platform.N8N: {
        "name": "n8n",
        "category": "iPaaS (source-available)",
        "best_for": ["app-to-app integration", "notifications", "lightweight orchestration"],
        "strengths": ["self-hostable", "code nodes", "large connector library", "low cost"],
    },
    Platform.WORKATO: {
        "name": "Workato",
        "category": "Enterprise iPaaS",
        "best_for": ["governed enterprise integration", "ERP/CRM recipes", "RPA bots"],
        "strengths": ["enterprise governance", "audit", "recipe lifecycle", "broad connectors"],
    },
    Platform.MAKE: {
        "name": "Make",
        "category": "iPaaS (visual)",
        "best_for": ["visual multi-step scenarios", "SMB integration"],
        "strengths": ["visual builder", "branching", "affordable"],
    },
    Platform.ZAPIER: {
        "name": "Zapier",
        "category": "iPaaS (simple)",
        "best_for": ["simple trigger→action automations", "fast time-to-value"],
        "strengths": ["huge app catalog", "no-code", "fastest to ship"],
    },
    Platform.LANGGRAPH: {
        "name": "LangGraph",
        "category": "Agent orchestration",
        "best_for": ["LLM agents", "stateful multi-step reasoning", "HITL graphs"],
        "strengths": ["graph state machine", "checkpointing", "human-in-the-loop", "tool use"],
    },
    Platform.TEMPORAL: {
        "name": "Temporal",
        "category": "Durable workflow engine",
        "best_for": ["long-running, mission-critical workflows", "exactly-once semantics"],
        "strengths": ["durable execution", "retries/compensation", "audit history", "scale"],
    },
    Platform.AIRFLOW: {
        "name": "Apache Airflow",
        "category": "Data orchestration",
        "best_for": ["batch data pipelines", "scheduled ETL/ELT"],
        "strengths": ["DAG scheduling", "data ecosystem", "backfills", "observability"],
    },
    Platform.NONE: {
        "name": "No automation platform",
        "category": "n/a",
        "best_for": ["steps that remain human-owned"],
        "strengths": [],
    },
}


def recommend_platform(automation_type: AutomationType, step: Any) -> tuple[Platform, list[Platform], str]:
    """Pick a platform for ``automation_type`` given a step's features."""
    if automation_type == AutomationType.HUMAN:
        return (
            Platform.NONE,
            [Platform.N8N],
            "Step remains human-owned; surrounding notifications/handoffs can be orchestrated "
            "in n8n, but the decision itself stays with a person.",
        )

    if automation_type == AutomationType.AGENT:
        alt = [Platform.TEMPORAL] if step.irreversible or step.financial_impact else [Platform.N8N]
        return (
            Platform.LANGGRAPH,
            alt,
            "Requires LLM reasoning, tool use, and human-in-the-loop checkpoints — LangGraph's "
            "stateful graph with checkpointing fits. "
            + (
                "Pair with Temporal for durable execution of the high-stakes side effects."
                if (step.irreversible or step.financial_impact)
                else "n8n can host the surrounding connectors."
            ),
        )

    if automation_type == AutomationType.WORKFLOW_ENGINE:
        if step.irreversible or step.financial_impact:
            return (
                Platform.TEMPORAL,
                [Platform.WORKATO],
                "Long-running and high-stakes (financial / irreversible) — Temporal's durable "
                "execution, retries, and compensation guarantee exactly-once side effects with a "
                "full audit history.",
            )
        if step.type.value in {"storage", "data_entry", "integration"}:
            return (
                Platform.AIRFLOW,
                [Platform.N8N, Platform.WORKATO],
                "Data-movement / batch step — Airflow's DAG scheduling, backfills, and data-stack "
                "integration are the right fit.",
            )
        return (
            Platform.N8N,
            [Platform.WORKATO, Platform.MAKE],
            "Multi-step orchestration without durable-execution requirements — n8n balances "
            "capability and cost; Workato if enterprise governance is mandatory.",
        )

    if automation_type == AutomationType.INTEGRATION:
        enterprise = any(s for s in step.systems if s in {"SAP", "Salesforce", "Workday", "NetSuite", "ServiceNow"})
        if enterprise:
            return (
                Platform.WORKATO,
                [Platform.N8N, Platform.MAKE],
                "Touches governed systems of record (ERP/CRM/HCM) — Workato provides enterprise "
                "connectors, recipe lifecycle, and audit controls.",
            )
        return (
            Platform.N8N,
            [Platform.ZAPIER, Platform.MAKE],
            "Straightforward app-to-app integration — n8n (self-hostable, low cost) is the "
            "default; Zapier/Make for the fastest no-code path.",
        )

    if automation_type == AutomationType.RPA:
        return (
            Platform.WORKATO,
            [Platform.N8N],
            "No first-class API exists, so UI-level automation (RPA) is required. Workato bundles "
            "RPA bots; flag a dedicated RPA tool (UiPath / Automation Anywhere) if UI surface is "
            "large. Prefer migrating to an API integration when one becomes available.",
        )

    return (Platform.N8N, [], "Default integration platform.")
