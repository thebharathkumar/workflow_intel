"""Governance Agent — automation-tier classification and the AI risk register."""

from __future__ import annotations

from workflow_intel.agents.base import Agent
from workflow_intel.agents.state import PipelineState
from workflow_intel.domain.enums import (
    GovernanceClass,
    Likelihood,
    RiskCategory,
    Severity,
    StepType,
)
from workflow_intel.domain.models import GovernanceClassification, RiskItem, WorkflowGraph, WorkflowStep
from workflow_intel.observability.tracing import Span


def _classify(step: WorkflowStep) -> tuple[GovernanceClass, str, list[str]]:
    if step.irreversible and step.financial_impact:
        return (
            GovernanceClass.PROHIBITED,
            "Irreversible action with direct financial impact (e.g., executing payment or signing). "
            "Must remain under human control; AI may prepare but not execute.",
            ["Dual human authorization", "Segregation of duties", "Immutable audit log"],
        )
    if step.type == StepType.APPROVAL or step.financial_impact or step.irreversible:
        return (
            GovernanceClass.HUMAN_APPROVAL,
            "Approval gate or materially significant action — automation may draft/queue, but a "
            "human must approve before commit.",
            ["Explicit human approval step", "Policy-based auto-approve only for low-risk cases", "Audit trail"],
        )
    if step.type in (StepType.REVIEW, StepType.DECISION) or step.touches_pii:
        return (
            GovernanceClass.HUMAN_REVIEW,
            "Judgment-heavy or PII-touching step — AI can perform the work, but outputs should be "
            "human-reviewed (at least on a sampled, risk-weighted basis).",
            ["Sampled human review", "Confidence-thresholded escalation", "PII redaction in logs"],
        )
    return (
        GovernanceClass.FULL_AUTOMATION,
        "Deterministic, low-risk step (notification / storage / system sync) with no financial, "
        "PII, or irreversibility concerns — safe to fully automate.",
        ["Standard monitoring & alerting", "Idempotent retries", "Rollback on failure"],
    )


class GovernanceAgent(Agent):
    name = "governance"

    async def _execute(self, state: PipelineState, span: Span) -> None:
        wf = state.workflow
        assert wf is not None
        state.governance = [
            GovernanceClassification(
                step_id=s.id,
                step_name=s.name,
                classification=(c := _classify(s))[0],
                rationale=c[1],
                controls=c[2],
            )
            for s in wf.steps
        ]
        state.risks = self._risks(wf)
        prohibited = sum(g.classification == GovernanceClass.PROHIBITED for g in state.governance)
        span.set(classified=len(state.governance), prohibited=prohibited, risks=len(state.risks))

    def _risks(self, wf: WorkflowGraph) -> list[RiskItem]:
        steps = wf.steps
        has_ai = any(s.type in (StepType.REVIEW, StepType.DECISION) for s in steps)
        has_external = any(s.is_external_comm for s in steps)
        has_pii = any(s.touches_pii for s in steps)
        has_financial = any(s.financial_impact for s in steps)
        has_irreversible_money = any(s.financial_impact and s.irreversible for s in steps)
        risks: list[RiskItem] = []

        if has_ai:
            risks.append(
                RiskItem(
                    category=RiskCategory.HALLUCINATION,
                    title="Model hallucination in AI-performed steps",
                    description="Agents performing review/decision steps may fabricate facts, citations, or conclusions.",
                    severity=Severity.HIGH if (has_financial or has_external) else Severity.MEDIUM,
                    likelihood=Likelihood.LIKELY,
                    mitigation="Ground outputs in retrieval with citations; enforce structured outputs; "
                    "faithfulness evals; confidence-thresholded human escalation.",
                )
            )
        if has_external or has_pii:
            risks.append(
                RiskItem(
                    category=RiskCategory.DATA_LEAKAGE,
                    title="Sensitive data exfiltration via outputs or tools",
                    description="External communication and document handling can leak confidential data through "
                    "model outputs, logs, or third-party tools.",
                    severity=Severity.HIGH if has_pii else Severity.MEDIUM,
                    likelihood=Likelihood.POSSIBLE,
                    mitigation="DLP scanning on egress, allow-listed tools, output redaction, tenant isolation, "
                    "no training on customer data.",
                )
            )
        if has_financial or has_pii or any("contract" in s.name.lower() for s in steps):
            risks.append(
                RiskItem(
                    category=RiskCategory.COMPLIANCE,
                    title="Regulatory/contractual non-compliance",
                    description="Financial, contractual, or personal-data processing carries SOX/GDPR/CCPA and "
                    "audit obligations that automated steps must satisfy.",
                    severity=Severity.HIGH,
                    likelihood=Likelihood.POSSIBLE,
                    mitigation="Immutable audit logs, human-approval gates, data-residency controls, periodic "
                    "control testing and evidence capture.",
                )
            )
        if has_pii:
            risks.append(
                RiskItem(
                    category=RiskCategory.PII,
                    title="Improper handling of personal data",
                    description="Steps process PII that could be over-retained, over-shared, or logged in clear text.",
                    severity=Severity.HIGH,
                    likelihood=Likelihood.LIKELY,
                    mitigation="Data minimization, field-level encryption, redaction before logging, retention "
                    "limits, and DSAR support.",
                )
            )
        if has_financial:
            risks.append(
                RiskItem(
                    category=RiskCategory.FINANCIAL,
                    title="Erroneous or unauthorized financial action",
                    description="Automated financial steps could post incorrect amounts or execute without authorization.",
                    severity=Severity.CRITICAL if has_irreversible_money else Severity.HIGH,
                    likelihood=Likelihood.POSSIBLE,
                    mitigation="Dual authorization, amount thresholds, reconciliation, dry-run + human approval "
                    "before commit, and compensating transactions.",
                )
            )
        # Operational risk always applies to an automated pipeline.
        risks.append(
            RiskItem(
                category=RiskCategory.OPERATIONAL,
                title="Automation/integration failure or drift",
                description="Integrations, agents, or workflow engines can fail, time out, or silently drift, "
                "stalling the process or producing partial state.",
                severity=Severity.MEDIUM,
                likelihood=Likelihood.LIKELY,
                mitigation="Health checks, idempotent retries with backoff, dead-letter queues, circuit breakers, "
                "on-call alerting, and a manual fallback path.",
            )
        )
        return risks
