"""Workflow Extraction Agent — turns prose into a typed :class:`WorkflowGraph`.

Uses the LLM provider for NL→structure when available (its strength), then runs the same
deterministic flag computation either way so downstream scoring/governance stays explainable.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from workflow_intel.agents.base import Agent
from workflow_intel.agents.state import PipelineState
from workflow_intel.analysis.heuristics import (
    ExtractedStep,
    ExtractedWorkflow,
    compute_step_flags,
    extract_workflow,
)
from workflow_intel.domain.enums import ActorType, EngineKind, HandoffMechanism, StepType
from workflow_intel.domain.models import Actor, Handoff, SystemRef, WorkflowGraph, WorkflowStep
from workflow_intel.knowledge.systems import match_systems
from workflow_intel.observability.tracing import Span

_SENDING_MECHANISMS = {
    HandoffMechanism.EMAIL,
    HandoffMechanism.CHAT,
    HandoffMechanism.NOTIFICATION,
    HandoffMechanism.TICKET,
    HandoffMechanism.FILE_UPLOAD,
    HandoffMechanism.API,
}


class _LLMStep(BaseModel):
    name: str
    description: str
    actor: str | None = None
    actor_type: ActorType = ActorType.HUMAN
    type: StepType = StepType.TASK
    systems: list[str] = Field(default_factory=list)
    mechanism: HandoffMechanism | None = None
    target_actor: str | None = None


class _LLMWorkflow(BaseModel):
    steps: list[_LLMStep]


_EXTRACTION_SYSTEM = (
    "You are a business-process analyst. Decompose the described workflow into ordered, atomic "
    "steps. For each step identify the acting actor and its type (human/team/system/agent/"
    "external), the step type, any named systems, the handoff mechanism, and the receiving actor."
)


class WorkflowExtractionAgent(Agent):
    name = "workflow_extraction"

    async def _execute(self, state: PipelineState, span: Span) -> None:
        extracted = await self._extract(state, span)
        state.extracted = extracted
        state.workflow = self._build_graph(extracted)
        span.set(
            steps=len(extracted.steps),
            actors=len(extracted.actors),
            systems=len(extracted.systems),
            engine=state.engine.value,
        )

    async def _extract(self, state: PipelineState, span: Span) -> ExtractedWorkflow:
        if state.provider.available:
            result = await state.provider.structured(_EXTRACTION_SYSTEM, state.source_text, _LLMWorkflow)
            if result is not None:
                span.set_tokens(result.input_tokens, result.output_tokens)
                state.engine = EngineKind.HYBRID
                state.model = result.model
                return self._from_llm(result.data)
        state.engine = EngineKind.DETERMINISTIC
        return extract_workflow(state.source_text)

    def _from_llm(self, data: _LLMWorkflow) -> ExtractedWorkflow:
        actors: dict[str, ActorType] = {}
        steps: list[ExtractedStep] = []
        previous_outputs: list[str] = []
        for i, raw in enumerate(data.steps, start=1):
            if raw.actor:
                actors[raw.actor] = raw.actor_type
            flags = compute_step_flags(raw.description, raw.type, raw.actor_type)
            step = ExtractedStep(
                id=f"S{i}",
                name=raw.name[:140],
                description=raw.description,
                type=raw.type,
                actor=raw.actor,
                actor_type=raw.actor_type,
                systems=raw.systems or [s["name"] for s in match_systems(raw.description)],
                order=i,
                mechanism=raw.mechanism,
                target_actor=raw.target_actor,
                inputs=list(previous_outputs),
                outputs=[],
                **flags,
            )
            steps.append(step)
            previous_outputs = step.systems[:1]
        systems = match_systems(" ".join(s.description for s in data.steps))
        return ExtractedWorkflow(steps=steps, actors=actors, systems=systems)

    def _build_graph(self, extracted: ExtractedWorkflow) -> WorkflowGraph:
        steps = [
            WorkflowStep(
                id=s.id,
                name=s.name,
                description=s.description,
                type=s.type,
                actor=s.actor,
                systems=s.systems,
                inputs=s.inputs,
                outputs=s.outputs,
                order=s.order,
                is_manual=s.is_manual,
                is_external_comm=s.is_external_comm,
                is_repetitive=s.is_repetitive,
                touches_pii=s.touches_pii,
                financial_impact=s.financial_impact,
                irreversible=s.irreversible,
            )
            for s in extracted.steps
        ]
        actors = [Actor(name=name, type=atype) for name, atype in extracted.actors.items()]
        systems = [
            SystemRef(name=s["name"], category=s.get("category", "application"), vendor=s.get("vendor"))
            for s in extracted.systems
        ]
        handoffs: list[Handoff] = []
        ordered = sorted(extracted.steps, key=lambda s: s.order)
        for a, b in zip(ordered, ordered[1:], strict=False):
            mechanism = (
                a.mechanism
                if a.mechanism in _SENDING_MECHANISMS
                else (b.mechanism if b.mechanism in _SENDING_MECHANISMS else HandoffMechanism.MANUAL)
            )
            handoffs.append(
                Handoff(
                    from_step=a.id,
                    to_step=b.id,
                    from_actor=a.actor,
                    to_actor=a.target_actor or b.actor,
                    mechanism=mechanism,
                )
            )
        return WorkflowGraph(steps=steps, actors=actors, systems=systems, handoffs=handoffs)
