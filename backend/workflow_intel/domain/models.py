"""Pydantic domain model — the single source of truth for every analysis output.

The aggregate root is :class:`AnalysisResult`. It is produced by the agent pipeline,
persisted by the repository, returned by the API, exported to JSON/YAML, and mirrored as
TypeScript types in the frontend.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import uuid4

from pydantic import BaseModel, Field, computed_field

from workflow_intel.domain.enums import (
    ActorType,
    AutomationType,
    BottleneckType,
    EngineKind,
    GovernanceClass,
    HandoffMechanism,
    Likelihood,
    Platform,
    RiskCategory,
    Severity,
    StepType,
)

Score = Annotated[int, Field(ge=0, le=100)]


def _now() -> datetime:
    return datetime.now(UTC)


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _san(text: str) -> str:
    """Sanitize a label so it is safe inside Mermaid node syntax."""
    return (
        text.replace('"', "'")
        .replace("[", "(")
        .replace("]", ")")
        .replace("{", "(")
        .replace("}", ")")
        .replace("\n", " ")
        .strip()
    )


# --------------------------------------------------------------------------- #
# Workflow structure
# --------------------------------------------------------------------------- #
class Actor(BaseModel):
    """A participant in the workflow (person, team, system, or agent)."""

    name: str
    type: ActorType = ActorType.HUMAN
    role: str | None = None


class SystemRef(BaseModel):
    """A system or application referenced by the workflow."""

    name: str
    category: str = "application"
    vendor: str | None = None


class Handoff(BaseModel):
    """A transition of work between two steps/actors and its mechanism."""

    from_step: str
    to_step: str
    from_actor: str | None = None
    to_actor: str | None = None
    mechanism: HandoffMechanism = HandoffMechanism.MANUAL
    description: str | None = None


class WorkflowStep(BaseModel):
    """A single, canonical unit of the business process."""

    id: str
    name: str
    description: str = ""
    type: StepType = StepType.TASK
    actor: str | None = None
    systems: list[str] = Field(default_factory=list)
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    order: int = 0
    # Feature flags drive scoring, governance, and risk downstream.
    is_manual: bool = False
    is_external_comm: bool = False
    is_repetitive: bool = False
    touches_pii: bool = False
    financial_impact: bool = False
    irreversible: bool = False


class WorkflowNode(BaseModel):
    """Visualization node (React Flow / JSON graph)."""

    id: str
    label: str
    type: str
    lane: str | None = None
    position: dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0})
    data: dict[str, Any] = Field(default_factory=dict)


class WorkflowEdge(BaseModel):
    """Visualization edge."""

    id: str
    source: str
    target: str
    label: str | None = None
    mechanism: HandoffMechanism | None = None


class WorkflowGraph(BaseModel):
    """The semantic workflow plus derived, multi-format graph renderings."""

    steps: list[WorkflowStep] = Field(default_factory=list)
    actors: list[Actor] = Field(default_factory=list)
    systems: list[SystemRef] = Field(default_factory=list)
    handoffs: list[Handoff] = Field(default_factory=list)

    # --- derived graph (kept in output so the frontend can render directly) ---
    @computed_field  # type: ignore[prop-decorator]
    @property
    def nodes(self) -> list[WorkflowNode]:
        lanes = {a.name: i for i, a in enumerate(self.actors)}
        nodes: list[WorkflowNode] = []
        for step in sorted(self.steps, key=lambda s: s.order):
            lane = step.actor or "unassigned"
            nodes.append(
                WorkflowNode(
                    id=step.id,
                    label=step.name,
                    type=step.type.value,
                    lane=lane,
                    position={"x": float(step.order * 240), "y": float(lanes.get(lane, 0) * 140)},
                    data={
                        "actor": step.actor,
                        "systems": step.systems,
                        "is_manual": step.is_manual,
                        "touches_pii": step.touches_pii,
                    },
                )
            )
        return nodes

    @computed_field  # type: ignore[prop-decorator]
    @property
    def edges(self) -> list[WorkflowEdge]:
        if self.handoffs:
            return [
                WorkflowEdge(
                    id=f"e_{h.from_step}_{h.to_step}",
                    source=h.from_step,
                    target=h.to_step,
                    label=h.mechanism.value,
                    mechanism=h.mechanism,
                )
                for h in self.handoffs
            ]
        ordered = sorted(self.steps, key=lambda s: s.order)
        return [
            WorkflowEdge(id=f"e_{a.id}_{b.id}", source=a.id, target=b.id)
            for a, b in zip(ordered, ordered[1:], strict=False)
        ]

    def to_reactflow(self) -> dict[str, Any]:
        return {
            "nodes": [
                {"id": n.id, "type": "default", "data": {"label": n.label, **n.data}, "position": n.position}
                for n in self.nodes
            ],
            "edges": [{"id": e.id, "source": e.source, "target": e.target, "label": e.label} for e in self.edges],
        }

    def to_json_graph(self) -> dict[str, Any]:
        """JSON Graph Format (nodes + edges with metadata)."""
        return {
            "graph": {
                "directed": True,
                "nodes": {n.id: {"label": n.label, "metadata": {"type": n.type, **n.data}} for n in self.nodes},
                "edges": [{"source": e.source, "target": e.target, "relation": e.label} for e in self.edges],
            }
        }

    def to_mermaid(self) -> str:
        shapes = {
            StepType.DECISION.value: ("{", "}"),
            StepType.APPROVAL.value: ("[/", "/]"),
            StepType.REVIEW.value: ("[/", "/]"),
            StepType.STORAGE.value: ("[(", ")]"),
            StepType.NOTIFICATION.value: (">", "]"),
            StepType.AGENT_ACTION.value: ("([", "])"),
        }
        lines = ["flowchart TD"]
        for n in self.nodes:
            open_b, close_b = shapes.get(n.type, ("[", "]"))
            lines.append(f'    {n.id}{open_b}"{_san(n.label)}"{close_b}')
        for e in self.edges:
            label = f"|{_san(e.label)}|" if e.label else ""
            lines.append(f"    {e.source} -->{label} {e.target}")
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Process intelligence
# --------------------------------------------------------------------------- #
class ProcessIntelligenceReport(BaseModel):
    summary: str
    business_objective: str
    participants: list[str] = Field(default_factory=list)
    systems: list[str] = Field(default_factory=list)
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    risk_areas: list[str] = Field(default_factory=list)


class Bottleneck(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("bn"))
    type: BottleneckType
    title: str
    description: str
    step_ids: list[str] = Field(default_factory=list)
    impact_score: Score = 50
    complexity_score: Score = 50
    confidence_score: Score = 50
    estimated_roi: str = "medium"
    annual_hours_saved: float = 0.0
    ai_capability: str | None = None  # e.g. classification, summarization, extraction
    recommendation: str = ""


# --------------------------------------------------------------------------- #
# Automation blueprint
# --------------------------------------------------------------------------- #
class AutomationRecommendation(BaseModel):
    step_id: str
    step_name: str
    automation_type: AutomationType
    suggested_platform: Platform
    alternative_platforms: list[Platform] = Field(default_factory=list)
    reasoning: str
    confidence_score: Score = 60
    prerequisites: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Agent architecture
# --------------------------------------------------------------------------- #
class AgentDesign(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("agent"))
    name: str
    purpose: str
    responsibilities: list[str] = Field(default_factory=list)
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    memory_requirements: list[str] = Field(default_factory=list)
    escalation_rules: list[str] = Field(default_factory=list)
    hitl_rules: list[str] = Field(default_factory=list)
    evaluation_metrics: list[str] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)
    recovery_strategy: str = ""
    guardrails: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Enterprise integration
# --------------------------------------------------------------------------- #
class Integration(BaseModel):
    system: str
    category: str = "application"
    vendor: str | None = None
    direction: str = "bidirectional"  # read | write | bidirectional
    api_requirements: list[str] = Field(default_factory=list)
    auth_methods: list[str] = Field(default_factory=list)
    event_triggers: list[str] = Field(default_factory=list)
    webhooks: list[str] = Field(default_factory=list)
    data_objects: list[str] = Field(default_factory=list)
    mcp_opportunity: str | None = None


# --------------------------------------------------------------------------- #
# Governance & risk
# --------------------------------------------------------------------------- #
class GovernanceClassification(BaseModel):
    step_id: str
    step_name: str
    classification: GovernanceClass
    rationale: str
    controls: list[str] = Field(default_factory=list)


_SEVERITY_WEIGHT = {Severity.LOW: 1, Severity.MEDIUM: 2, Severity.HIGH: 3, Severity.CRITICAL: 4}
_LIKELIHOOD_WEIGHT = {
    Likelihood.RARE: 1,
    Likelihood.UNLIKELY: 2,
    Likelihood.POSSIBLE: 3,
    Likelihood.LIKELY: 4,
    Likelihood.ALMOST_CERTAIN: 5,
}


class RiskItem(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("risk"))
    category: RiskCategory
    title: str
    description: str
    severity: Severity = Severity.MEDIUM
    likelihood: Likelihood = Likelihood.POSSIBLE
    mitigation: str = ""
    owner: str = "AI Governance"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def risk_score(self) -> int:
        """1–20 composite (severity × likelihood)."""
        return _SEVERITY_WEIGHT[self.severity] * _LIKELIHOOD_WEIGHT[self.likelihood]


# --------------------------------------------------------------------------- #
# Observability
# --------------------------------------------------------------------------- #
class ObservabilitySignal(BaseModel):
    name: str
    telemetry_type: str  # metric | trace | log
    description: str
    otel_instrument: str | None = None
    unit: str | None = None


class Dashboard(BaseModel):
    name: str
    tool: str
    panels: list[str] = Field(default_factory=list)


class ObservabilitySpec(BaseModel):
    signals: list[ObservabilitySignal] = Field(default_factory=list)
    tools: list[dict[str, str]] = Field(default_factory=list)
    dashboards: list[Dashboard] = Field(default_factory=list)
    slos: list[dict[str, str]] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Evaluation
# --------------------------------------------------------------------------- #
class EvaluationSpec(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("eval"))
    name: str
    target: str  # workflow | agent | routing | tool_selection | escalation | automation_success
    description: str
    metric: str
    kpi_target: str
    method: str
    dataset: str = "curated golden set"
    cadence: str = "per release + nightly"


# --------------------------------------------------------------------------- #
# Observability traces (captured at runtime)
# --------------------------------------------------------------------------- #
class AgentTrace(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    agent: str
    status: str = "ok"  # ok | error
    started_at: datetime = Field(default_factory=_now)
    latency_ms: float = 0.0
    token_estimate: int = 0
    cost_usd_estimate: float = 0.0
    error: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Aggregate root
# --------------------------------------------------------------------------- #
class AnalysisResult(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("wf"))
    created_at: datetime = Field(default_factory=_now)
    source_text: str
    engine: EngineKind = EngineKind.DETERMINISTIC
    model: str | None = None

    process_report: ProcessIntelligenceReport
    workflow: WorkflowGraph
    bottlenecks: list[Bottleneck] = Field(default_factory=list)
    automations: list[AutomationRecommendation] = Field(default_factory=list)
    agents: list[AgentDesign] = Field(default_factory=list)
    integrations: list[Integration] = Field(default_factory=list)
    governance: list[GovernanceClassification] = Field(default_factory=list)
    risks: list[RiskItem] = Field(default_factory=list)
    observability: ObservabilitySpec = Field(default_factory=ObservabilitySpec)
    evaluation: list[EvaluationSpec] = Field(default_factory=list)
    diagrams: dict[str, str] = Field(default_factory=dict)
    trace: list[AgentTrace] = Field(default_factory=list)

    def summary(self) -> AnalysisSummary:
        return AnalysisSummary(
            id=self.id,
            created_at=self.created_at,
            engine=self.engine,
            title=self.process_report.summary[:120],
            step_count=len(self.workflow.steps),
            actor_count=len(self.workflow.actors),
            system_count=len(self.workflow.systems),
            bottleneck_count=len(self.bottlenecks),
            agent_count=len(self.agents),
            risk_count=len(self.risks),
        )


class AnalysisSummary(BaseModel):
    """Lightweight projection for list views."""

    id: str
    created_at: datetime
    engine: EngineKind
    title: str
    step_count: int
    actor_count: int
    system_count: int
    bottleneck_count: int
    agent_count: int
    risk_count: int
