"""Automation Architect Agent — per-step automation type, platform, and agent designs."""

from __future__ import annotations

from workflow_intel.agents.base import Agent
from workflow_intel.agents.intelligence import ai_capability
from workflow_intel.agents.state import PipelineState
from workflow_intel.domain.enums import AutomationType, StepType
from workflow_intel.domain.models import AgentDesign, AutomationRecommendation, WorkflowStep
from workflow_intel.knowledge.platforms import recommend_platform
from workflow_intel.observability.tracing import Span


def _automation_type(step: WorkflowStep) -> AutomationType:
    if step.type == StepType.APPROVAL:
        return AutomationType.HUMAN
    if step.type in (StepType.REVIEW, StepType.DECISION):
        return AutomationType.AGENT
    if step.type == StepType.DATA_ENTRY:
        return AutomationType.INTEGRATION if step.systems else AutomationType.RPA
    if step.type in (StepType.STORAGE, StepType.INTEGRATION, StepType.NOTIFICATION):
        return AutomationType.INTEGRATION
    # Generic task: prefer integration when a system is involved, else a workflow engine.
    return AutomationType.INTEGRATION if step.systems else AutomationType.WORKFLOW_ENGINE


def _agent_design(step: WorkflowStep, capability: str) -> AgentDesign:
    pretty = capability.replace("_", " ").title()
    name = {
        "contract_review": "Contract Review Agent",
        "document_review": "Document Review Agent",
        "ticket_triage_and_routing": "Ticket Triage Agent",
        "classification_and_routing": "Routing & Classification Agent",
        "summarization": "Summarization Agent",
        "data_extraction": "Data Extraction Agent",
    }.get(capability, f"{pretty} Agent")

    needs_approval = step.financial_impact or step.irreversible or step.touches_pii
    tools = [f"{sys} (MCP tool)" for sys in step.systems] or ["Document store (read)", "Notification channel"]
    tools.append("retrieval over policy/templates")

    return AgentDesign(
        name=name,
        purpose=f"Perform {pretty.lower()} for the step '{step.name}' with human oversight.",
        responsibilities=[
            f"Ingest the work item for '{step.name}'",
            f"Apply {pretty.lower()} against policy, prior examples, and templates",
            "Produce a structured recommendation with citations and a confidence score",
            "Escalate low-confidence or high-risk items to a human",
        ],
        inputs=step.inputs or ["upstream artifact", "policy/context"],
        outputs=(step.outputs or ["recommendation"]) + ["confidence_score", "rationale"],
        tools=tools,
        memory_requirements=[
            "Short-term: current case context window",
            "Long-term: vector store of prior decisions, policies, and templates",
            "Episodic: audit log of past actions for traceability",
        ],
        escalation_rules=[
            "Confidence below threshold (e.g., < 0.8) → route to human",
            "Detected anomaly or out-of-policy condition → escalate with reason",
        ]
        + (["Any financially or legally material decision → mandatory human approval"] if needs_approval else []),
        hitl_rules=[
            "Human approval required before any irreversible/external action"
            if needs_approval
            else "Human review recommended on a sampled basis",
            "Reviewer can accept, edit, or reject; edits feed back as training signal",
        ],
        evaluation_metrics=[
            "Decision accuracy vs. human gold labels",
            "Escalation precision/recall",
            "Citation/faithfulness (groundedness) rate",
            "Mean time-to-decision",
        ],
        failure_modes=[
            "Hallucinated facts or fabricated citations",
            "Misclassification / wrong route",
            "Tool/integration timeout or partial write",
            "Prompt-injection via untrusted document content",
        ],
        recovery_strategy=(
            "Retry idempotent tool calls with backoff; on repeated failure, fall back to human "
            "queue; never leave a partial write — wrap side effects in a compensating transaction."
        ),
        guardrails=[
            "Output constrained to a validated schema (structured outputs)",
            "Allow-listed tools only; no free-form code execution",
            "PII redaction before logging" if step.touches_pii else "Log redaction for secrets",
        ],
    )


class AutomationArchitectAgent(Agent):
    name = "automation_architect"

    async def _execute(self, state: PipelineState, span: Span) -> None:
        wf = state.workflow
        assert wf is not None
        recs: list[AutomationRecommendation] = []
        designs: dict[str, AgentDesign] = {}

        for step in wf.steps:
            atype = _automation_type(step)
            platform, alternatives, platform_reason = recommend_platform(atype, step)
            reasoning = f"Step type '{step.type.value}' → {atype.value.replace('_', ' ')}. {platform_reason}"
            recs.append(
                AutomationRecommendation(
                    step_id=step.id,
                    step_name=step.name,
                    automation_type=atype,
                    suggested_platform=platform,
                    alternative_platforms=alternatives,
                    reasoning=reasoning,
                    confidence_score=78 if step.systems else 64,
                    prerequisites=self._prereqs(step, atype),
                )
            )
            if atype == AutomationType.AGENT:
                design = _agent_design(step, ai_capability(step))
                designs.setdefault(design.name, design)

        state.automations = recs
        state.agents = list(designs.values())
        span.set(
            recommendations=len(recs),
            agents_designed=len(designs),
            agentic=sum(r.automation_type == AutomationType.AGENT for r in recs),
        )

    def _prereqs(self, step: WorkflowStep, atype: AutomationType) -> list[str]:
        prereqs: list[str] = []
        if atype == AutomationType.INTEGRATION and step.systems:
            prereqs.append(f"API credentials & scopes for {', '.join(step.systems)}")
        if atype == AutomationType.AGENT:
            prereqs += ["Evaluation/golden dataset", "Guardrails & HITL queue", "Tool/MCP definitions"]
        if atype == AutomationType.RPA:
            prereqs.append("Stable UI selectors or a vendor API roadmap")
        if step.touches_pii:
            prereqs.append("DLP / PII-handling sign-off")
        return prereqs
