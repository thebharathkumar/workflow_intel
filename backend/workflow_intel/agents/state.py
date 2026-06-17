"""Shared mutable state threaded through the agent pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field

from workflow_intel.analysis.heuristics import ExtractedWorkflow
from workflow_intel.config import Settings
from workflow_intel.domain.enums import EngineKind
from workflow_intel.domain.models import (
    AgentDesign,
    AutomationRecommendation,
    Bottleneck,
    EvaluationSpec,
    GovernanceClassification,
    Integration,
    ObservabilitySpec,
    ProcessIntelligenceReport,
    RiskItem,
    WorkflowGraph,
)
from workflow_intel.llm.provider import LLMProvider
from workflow_intel.observability.tracing import SpanRecorder


@dataclass
class PipelineState:
    """Carries inputs, the LLM provider, the trace recorder, and accumulating outputs."""

    source_text: str
    recorder: SpanRecorder
    provider: LLMProvider
    settings: Settings

    engine: EngineKind = EngineKind.DETERMINISTIC
    model: str | None = None

    extracted: ExtractedWorkflow | None = None
    workflow: WorkflowGraph | None = None
    process_report: ProcessIntelligenceReport | None = None
    bottlenecks: list[Bottleneck] = field(default_factory=list)
    automations: list[AutomationRecommendation] = field(default_factory=list)
    agents: list[AgentDesign] = field(default_factory=list)
    integrations: list[Integration] = field(default_factory=list)
    governance: list[GovernanceClassification] = field(default_factory=list)
    risks: list[RiskItem] = field(default_factory=list)
    observability: ObservabilitySpec | None = None
    evaluation: list[EvaluationSpec] = field(default_factory=list)
    diagrams: dict[str, str] = field(default_factory=dict)
