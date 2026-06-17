"""Process Intelligence Agent — efficiency report + scored bottleneck detection."""

from __future__ import annotations

from workflow_intel.agents.base import Agent
from workflow_intel.agents.state import PipelineState
from workflow_intel.domain.enums import BottleneckType, HandoffMechanism, StepType
from workflow_intel.domain.models import (
    Bottleneck,
    ProcessIntelligenceReport,
    WorkflowGraph,
    WorkflowStep,
)
from workflow_intel.observability.tracing import Span

_AI_CAPABILITY = {
    StepType.REVIEW: "document_review",
    StepType.DECISION: "classification_and_routing",
}


def _roi_label(impact: int, complexity: int) -> str:
    if impact >= 70 and complexity <= 50:
        return "high"
    if impact >= 60:
        return "medium-high"
    if impact >= 45:
        return "medium"
    return "low"


def ai_capability(step: WorkflowStep) -> str:
    text = f"{step.name} {step.description}".lower()
    if "summar" in text:
        return "summarization"
    if "extract" in text or "data from" in text:
        return "data_extraction"
    if "triage" in text or "route" in text or "prioriti" in text:
        return "ticket_triage_and_routing"
    if "contract" in text and step.type == StepType.REVIEW:
        return "contract_review"
    return _AI_CAPABILITY.get(step.type, "classification")


class ProcessIntelligenceAgent(Agent):
    name = "process_intelligence"

    async def _execute(self, state: PipelineState, span: Span) -> None:
        wf = state.workflow
        assert wf is not None
        state.process_report = self._report(wf)
        state.bottlenecks = self._bottlenecks(wf)
        span.set(
            bottlenecks=len(state.bottlenecks),
            ai_candidates=sum(b.type == BottleneckType.AI_CANDIDATE for b in state.bottlenecks),
        )

    def _report(self, wf: WorkflowGraph) -> ProcessIntelligenceReport:
        actor_names = [a.name for a in wf.actors]
        system_names = [s.name for s in wf.systems]
        first = wf.steps[0] if wf.steps else None
        last = wf.steps[-1] if wf.steps else None

        objective = self._objective(wf)
        dependencies: list[str] = []
        for h in wf.handoffs:
            if h.mechanism in (HandoffMechanism.MANUAL, HandoffMechanism.EMAIL, HandoffMechanism.CHAT):
                dependencies.append(
                    f"Handoff from {h.from_actor or 'previous'} to {h.to_actor or 'next'} "
                    f"via {h.mechanism.value} (no system integration)"
                )
        for s in wf.systems:
            dependencies.append(f"Dependency on {s.name} ({s.category})")

        risk_areas: list[str] = []
        if any(s.is_manual for s in wf.steps):
            risk_areas.append("Manual data handling introduces error and latency risk")
        if any(s.is_external_comm for s in wf.steps):
            risk_areas.append("External communication path — data-leakage and brand risk")
        if any(s.touches_pii for s in wf.steps):
            risk_areas.append("PII handling — privacy/compliance exposure")
        if any(s.financial_impact for s in wf.steps):
            risk_areas.append("Financial impact — requires segregation of duties and approval")
        if any(h.mechanism in (HandoffMechanism.EMAIL, HandoffMechanism.MANUAL) for h in wf.handoffs):
            risk_areas.append("Manual/email handoffs create single points of delay")

        summary = (
            f"A {len(wf.steps)}-step workflow involving "
            f"{len(actor_names)} participant(s) ({', '.join(actor_names) or 'unspecified'}) "
            f"across {len(system_names)} system(s) ({', '.join(system_names) or 'none named'})."
        )
        return ProcessIntelligenceReport(
            summary=summary,
            business_objective=objective,
            participants=actor_names,
            systems=system_names,
            inputs=(first.inputs or first.outputs) if first else [],
            outputs=(last.outputs or []) if last else [],
            dependencies=dependencies,
            risk_areas=risk_areas or ["No material risks detected by heuristics"],
        )

    def _objective(self, wf: WorkflowGraph) -> str:
        text = " ".join(f"{s.name} {s.description}" for s in wf.steps).lower()
        if "contract" in text:
            return "Move a contract through review, approval, and system-of-record updates with full auditability."
        if "ticket" in text or "incident" in text:
            return "Triage, route, and resolve inbound requests while keeping stakeholders informed."
        if "invoice" in text or "payment" in text:
            return "Process financial documents accurately with the required approvals and controls."
        actors = [a.name for a in wf.actors]
        if actors:
            return f"Coordinate work end-to-end from {actors[0]} through {actors[-1]} with reliable handoffs."
        return "Coordinate the described business process end-to-end with reliable handoffs."

    def _bottlenecks(self, wf: WorkflowGraph) -> list[Bottleneck]:
        out: list[Bottleneck] = []

        for step in wf.steps:
            # AI-candidate opportunities (review / decision / summarize / extract / triage).
            if step.type in (StepType.REVIEW, StepType.DECISION):
                capability = ai_capability(step)
                impact = min(95, 55 + 15 * step.is_repetitive + 10 * step.financial_impact + 10 * step.is_external_comm)
                complexity = 65 + 10 * step.financial_impact + 10 * step.irreversible
                out.append(
                    Bottleneck(
                        type=BottleneckType.AI_CANDIDATE,
                        title=f"AI candidate: {capability.replace('_', ' ')} at '{step.name[:48]}'",
                        description=(
                            f"Step '{step.name}' is a {step.type.value} performed by "
                            f"{step.actor or 'a person'} — a strong fit for an AI agent performing "
                            f"{capability.replace('_', ' ')} with human oversight."
                        ),
                        step_ids=[step.id],
                        impact_score=impact,
                        complexity_score=min(95, complexity),
                        confidence_score=72,
                        estimated_roi=_roi_label(impact, complexity),
                        annual_hours_saved=260.0 if step.is_repetitive else 130.0,
                        ai_capability=capability,
                        recommendation=(
                            f"Introduce an agent to draft/triage; keep a human "
                            f"{'approver' if step.financial_impact or step.irreversible else 'reviewer'} in the loop."
                        ),
                    )
                )
            # Human bottleneck: manual approvals.
            if step.type == StepType.APPROVAL:
                impact = 70 + 10 * step.financial_impact
                out.append(
                    Bottleneck(
                        type=BottleneckType.HUMAN,
                        title=f"Manual approval gate at '{step.name[:48]}'",
                        description=f"Approval by {step.actor or 'a person'} can stall the workflow waiting on availability.",
                        step_ids=[step.id],
                        impact_score=min(95, impact),
                        complexity_score=40,
                        confidence_score=80,
                        estimated_roi=_roi_label(impact, 40),
                        annual_hours_saved=80.0,
                        recommendation="Add SLA timers, delegation, and a mobile approval path; auto-approve low-risk cases under policy.",
                    )
                )
            # System bottleneck: manual data entry / re-entry.
            if step.type == StepType.DATA_ENTRY and step.is_manual:
                impact = 75 if step.is_repetitive else 60
                out.append(
                    Bottleneck(
                        type=BottleneckType.SYSTEM,
                        title=f"Manual data entry at '{step.name[:48]}'",
                        description=(
                            f"Data is keyed manually into "
                            f"{', '.join(step.systems) or 'a system'} — duplicate effort and a common error source."
                        ),
                        step_ids=[step.id],
                        impact_score=impact,
                        complexity_score=35,
                        confidence_score=85,
                        estimated_roi=_roi_label(impact, 35),
                        annual_hours_saved=312.0 if step.is_repetitive else 156.0,
                        recommendation="Replace re-entry with an API/iPaaS integration so the record syncs automatically.",
                    )
                )

        # System bottleneck: missing integrations across manual/email handoffs.
        step_by_id = {s.id: s for s in wf.steps}
        for h in wf.handoffs:
            if h.mechanism not in (
                HandoffMechanism.MANUAL,
                HandoffMechanism.EMAIL,
                HandoffMechanism.CHAT,
                HandoffMechanism.FILE_UPLOAD,
            ):
                continue
            a, b = step_by_id.get(h.from_step), step_by_id.get(h.to_step)
            systems = sorted({*(a.systems if a else []), *(b.systems if b else [])})
            if h.mechanism == HandoffMechanism.EMAIL:
                out.append(
                    Bottleneck(
                        type=BottleneckType.HUMAN,
                        title=f"Email-based handoff ({h.from_actor or '?'} → {h.to_actor or '?'})",
                        description="Work is passed by email, creating delay, lost context, and no audit trail.",
                        step_ids=[h.from_step, h.to_step],
                        impact_score=65,
                        complexity_score=30,
                        confidence_score=78,
                        estimated_roi=_roi_label(65, 30),
                        annual_hours_saved=104.0,
                        recommendation="Replace the email handoff with a tracked task/queue or a system-to-system trigger.",
                    )
                )
            if len(systems) >= 2:
                out.append(
                    Bottleneck(
                        type=BottleneckType.SYSTEM,
                        title=f"Missing integration: {' ↔ '.join(systems[:2])}",
                        description=f"{' and '.join(systems[:2])} are bridged manually; an integration would remove the gap.",
                        step_ids=[h.from_step, h.to_step],
                        impact_score=72,
                        complexity_score=55,
                        confidence_score=70,
                        estimated_roi=_roi_label(72, 55),
                        annual_hours_saved=140.0,
                        recommendation=f"Build an event-driven integration between {systems[0]} and {systems[1]}.",
                    )
                )

        # Duplicate-systems (overlapping categories).
        by_category: dict[str, list[str]] = {}
        for s in wf.systems:
            by_category.setdefault(s.category, []).append(s.name)
        for category, names in by_category.items():
            if len(names) >= 2:
                out.append(
                    Bottleneck(
                        type=BottleneckType.SYSTEM,
                        title=f"Overlapping systems in '{category}'",
                        description=f"{' and '.join(names)} overlap in the {category} category — potential consolidation.",
                        impact_score=55,
                        complexity_score=70,
                        confidence_score=60,
                        estimated_roi=_roi_label(55, 70),
                        annual_hours_saved=0.0,
                        recommendation="Evaluate consolidating onto a single system of record for this category.",
                    )
                )

        return out
