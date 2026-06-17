"""Enumerations used throughout the domain model.

All enums are string-valued so they serialize cleanly to JSON/YAML and map 1:1 to the
TypeScript union types consumed by the frontend.
"""

from __future__ import annotations

from enum import StrEnum


class EngineKind(StrEnum):
    """Which engine produced an analysis."""

    DETERMINISTIC = "deterministic"
    LLM = "llm"
    HYBRID = "hybrid"


class ActorType(StrEnum):
    """The nature of a workflow participant."""

    HUMAN = "human"
    TEAM = "team"
    SYSTEM = "system"
    AGENT = "agent"
    EXTERNAL = "external"


class StepType(StrEnum):
    """Classification of a workflow step."""

    TASK = "task"
    DECISION = "decision"
    APPROVAL = "approval"
    REVIEW = "review"
    NOTIFICATION = "notification"
    DATA_ENTRY = "data_entry"
    STORAGE = "storage"
    INTEGRATION = "integration"
    AGENT_ACTION = "agent_action"


class HandoffMechanism(StrEnum):
    """How work passes between actors/steps."""

    EMAIL = "email"
    CHAT = "chat"
    MEETING = "meeting"
    TICKET = "ticket"
    FILE_UPLOAD = "file_upload"
    API = "api"
    NOTIFICATION = "notification"
    MANUAL = "manual"


class AutomationType(StrEnum):
    """Recommended execution model for a step."""

    HUMAN = "human"
    AGENT = "agent"
    WORKFLOW_ENGINE = "workflow_engine"
    INTEGRATION = "integration"
    RPA = "rpa"


class Platform(StrEnum):
    """Suggested implementation platform."""

    N8N = "n8n"
    WORKATO = "workato"
    MAKE = "make"
    ZAPIER = "zapier"
    LANGGRAPH = "langgraph"
    TEMPORAL = "temporal"
    AIRFLOW = "airflow"
    NONE = "none"


class BottleneckType(StrEnum):
    """Category of detected bottleneck / opportunity."""

    HUMAN = "human"
    SYSTEM = "system"
    AI_CANDIDATE = "ai_candidate"


class GovernanceClass(StrEnum):
    """Automation-governance tier for a step."""

    FULL_AUTOMATION = "safe_for_full_automation"
    HUMAN_APPROVAL = "human_approval_required"
    HUMAN_REVIEW = "human_review_recommended"
    PROHIBITED = "prohibited_automation"


class RiskCategory(StrEnum):
    """AI risk taxonomy."""

    HALLUCINATION = "hallucination"
    DATA_LEAKAGE = "data_leakage"
    COMPLIANCE = "compliance"
    PII = "pii"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Likelihood(StrEnum):
    RARE = "rare"
    UNLIKELY = "unlikely"
    POSSIBLE = "possible"
    LIKELY = "likely"
    ALMOST_CERTAIN = "almost_certain"
