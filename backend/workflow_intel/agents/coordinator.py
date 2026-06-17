"""Coordinator — canonical orchestrator of the agent DAG.

Runs extraction, fans out the analysis agents, then synthesizes. When ``use_langgraph`` is set
and LangGraph is installed, execution is delegated to an equivalent ``StateGraph`` that wraps the
same agent instances (see ``graph/langgraph_flow.py``); otherwise this orchestrator runs directly.
"""

from __future__ import annotations

import asyncio

from workflow_intel.agents.automation import AutomationArchitectAgent
from workflow_intel.agents.diagram import DiagramGenerationAgent
from workflow_intel.agents.evaluation import EvaluationAgent
from workflow_intel.agents.extraction import WorkflowExtractionAgent
from workflow_intel.agents.governance import GovernanceAgent
from workflow_intel.agents.integration import IntegrationAgent
from workflow_intel.agents.intelligence import ProcessIntelligenceAgent
from workflow_intel.agents.observability_agent import ObservabilityAgent
from workflow_intel.agents.state import PipelineState
from workflow_intel.config import Settings, get_settings
from workflow_intel.domain.models import AnalysisResult, ObservabilitySpec
from workflow_intel.llm.provider import LLMProvider, get_provider
from workflow_intel.observability.tracing import SpanRecorder


class Coordinator:
    """Builds and runs the multi-agent analysis pipeline."""

    def __init__(self, settings: Settings | None = None, provider: LLMProvider | None = None) -> None:
        self.settings = settings or get_settings()
        self.provider = provider or get_provider(self.settings)
        self.extraction = WorkflowExtractionAgent()
        self.intelligence = ProcessIntelligenceAgent()
        self.automation = AutomationArchitectAgent()
        self.governance = GovernanceAgent()
        self.integration = IntegrationAgent()
        self.observability = ObservabilityAgent()
        self.evaluation = EvaluationAgent()
        self.diagram = DiagramGenerationAgent()

    async def analyze(self, text: str) -> AnalysisResult:
        state = PipelineState(
            source_text=text,
            recorder=SpanRecorder(),
            provider=self.provider,
            settings=self.settings,
        )

        if self.settings.use_langgraph:
            try:
                from workflow_intel.graph.langgraph_flow import run_with_langgraph

                await run_with_langgraph(self, state)
            except Exception:
                await self._run(state)
        else:
            await self._run(state)

        return self._assemble(state)

    async def _run(self, state: PipelineState) -> None:
        """The canonical DAG."""
        await self.extraction.run(state)
        await self.intelligence.run(state)
        await asyncio.gather(self.automation.run(state), self.integration.run(state))
        await self.governance.run(state)
        await asyncio.gather(self.observability.run(state), self.evaluation.run(state))
        await self.diagram.run(state)

    def _assemble(self, state: PipelineState) -> AnalysisResult:
        assert state.workflow is not None and state.process_report is not None
        return AnalysisResult(
            source_text=state.source_text,
            engine=state.engine,
            model=state.model,
            process_report=state.process_report,
            workflow=state.workflow,
            bottlenecks=state.bottlenecks,
            automations=state.automations,
            agents=state.agents,
            integrations=state.integrations,
            governance=state.governance,
            risks=state.risks,
            observability=state.observability or ObservabilitySpec(),
            evaluation=state.evaluation,
            diagrams=state.diagrams,
            trace=state.recorder.traces,
        )
