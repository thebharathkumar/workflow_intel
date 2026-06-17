"""Exercises the optional LangGraph StateGraph adapter.

Skipped automatically when the `graph` extra (langgraph) is not installed; runs in the
`backend-extras` CI job where it is.
"""

import pytest

from workflow_intel.agents.coordinator import Coordinator
from workflow_intel.agents.state import PipelineState
from workflow_intel.config import Settings
from workflow_intel.llm.provider import NullProvider
from workflow_intel.observability.tracing import SpanRecorder


async def test_langgraph_flow_runs_directly(example_text):
    pytest.importorskip("langgraph")
    from workflow_intel.graph.langgraph_flow import run_with_langgraph

    coordinator = Coordinator(Settings(llm_enabled=False))
    state = PipelineState(
        source_text=example_text,
        recorder=SpanRecorder(),
        provider=NullProvider(),
        settings=coordinator.settings,
    )
    await run_with_langgraph(coordinator, state)

    assert state.workflow is not None and len(state.workflow.steps) >= 4
    assert state.process_report is not None
    assert state.diagrams and "system" in state.diagrams
    # One span per agent recorded through the StateGraph nodes.
    assert len(state.recorder.traces) >= 8


async def test_coordinator_uses_langgraph_when_enabled(example_text):
    pytest.importorskip("langgraph")
    coordinator = Coordinator(Settings(llm_enabled=False, use_langgraph=True))
    result = await coordinator.analyze(example_text)

    assert len(result.workflow.steps) >= 4
    assert {"workflow_extraction", "governance", "diagram_generation"} <= {t.agent for t in result.trace}
