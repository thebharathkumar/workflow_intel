"""Evaluation Agent — measurable evals and KPIs across the system."""

from __future__ import annotations

from workflow_intel.agents.base import Agent
from workflow_intel.agents.state import PipelineState
from workflow_intel.domain.models import EvaluationSpec
from workflow_intel.observability.tracing import Span


class EvaluationAgent(Agent):
    name = "evaluation"

    async def _execute(self, state: PipelineState, span: Span) -> None:
        specs = [
            EvaluationSpec(
                name="Workflow extraction accuracy",
                target="workflow",
                description="Does the extracted graph match the analyst-labeled ground truth?",
                metric="Step/actor/system F1 vs. golden annotations",
                kpi_target="F1 ≥ 0.90",
                method="Golden dataset of labeled descriptions; structural diff against extraction.",
            ),
            EvaluationSpec(
                name="Agent decision accuracy",
                target="agent",
                description="Agreement of agent decisions with human expert labels.",
                metric="Accuracy / Cohen's κ vs. expert",
                kpi_target="Accuracy ≥ 0.90, κ ≥ 0.8",
                method="Blind replay on a held-out case set; expert adjudication of disagreements.",
            ),
            EvaluationSpec(
                name="Routing accuracy",
                target="routing",
                description="Correctness of triage/routing decisions to the right queue/owner.",
                metric="Top-1 routing accuracy",
                kpi_target="≥ 0.92",
                method="Confusion matrix over labeled routing outcomes; per-class recall floor.",
            ),
            EvaluationSpec(
                name="Tool selection correctness",
                target="tool_selection",
                description="Does the agent pick the correct tool/integration with valid arguments?",
                metric="Tool-choice accuracy + argument-validity rate",
                kpi_target="≥ 0.95 valid calls",
                method="Trajectory eval over recorded tool calls; schema validation of arguments.",
            ),
            EvaluationSpec(
                name="Human escalation decisions",
                target="escalation",
                description="Does the agent escalate exactly when it should (no over/under-escalation)?",
                metric="Escalation precision & recall",
                kpi_target="Precision ≥ 0.85, Recall ≥ 0.90",
                method="Labeled should-escalate set; threshold sweep to set the confidence cutoff.",
            ),
            EvaluationSpec(
                name="Automation success rate",
                target="automation_success",
                description="End-to-end completion without human correction or rollback.",
                metric="Straight-through-processing (STP) rate",
                kpi_target="≥ 0.80 STP, < 2% rollback",
                method="Production cohort analysis; track corrections, rollbacks, and reopen rate.",
            ),
            EvaluationSpec(
                name="Groundedness / faithfulness",
                target="agent",
                description="Are agent claims supported by retrieved sources (anti-hallucination)?",
                metric="Faithfulness score (LLM-judge + citation check)",
                kpi_target="≥ 0.95",
                method="Citation verification + LLM-as-judge with a calibrated rubric.",
            ),
        ]
        state.evaluation = specs
        span.set(evals=len(specs))
