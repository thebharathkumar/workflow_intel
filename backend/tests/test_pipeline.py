import pytest

from workflow_intel.agents.coordinator import Coordinator
from workflow_intel.config import Settings
from workflow_intel.domain.enums import BottleneckType, EngineKind


@pytest.fixture
def coordinator() -> Coordinator:
    return Coordinator(Settings(llm_enabled=False))


async def test_full_pipeline_shape(coordinator, example_text):
    result = await coordinator.analyze(example_text)

    assert result.engine == EngineKind.DETERMINISTIC
    assert result.process_report.summary
    assert len(result.workflow.steps) >= 4
    assert result.bottlenecks
    assert result.automations and len(result.automations) == len(result.workflow.steps)
    assert result.integrations  # Salesforce / Slack / SharePoint
    assert len(result.governance) == len(result.workflow.steps)
    assert result.risks
    assert result.observability.signals
    assert result.evaluation


async def test_pipeline_designs_agent_for_review(coordinator, example_text):
    result = await coordinator.analyze(example_text)
    # Legal review → AI candidate → at least one designed agent.
    assert result.agents
    assert any(b.type == BottleneckType.AI_CANDIDATE for b in result.bottlenecks)
    a = result.agents[0]
    assert a.responsibilities and a.escalation_rules and a.failure_modes and a.recovery_strategy


async def test_pipeline_emits_all_diagrams(coordinator, example_text):
    result = await coordinator.analyze(example_text)
    for kind in ("workflow", "system", "agent", "data_flow", "sequence", "integration"):
        assert kind in result.diagrams
        assert result.diagrams[kind].strip()
    assert result.workflow.to_mermaid().startswith("flowchart")


async def test_pipeline_captures_one_trace_per_agent(coordinator, example_text):
    result = await coordinator.analyze(example_text)
    agents_traced = {t.agent for t in result.trace}
    assert {
        "workflow_extraction",
        "process_intelligence",
        "automation_architect",
        "governance",
        "integration",
        "observability",
        "evaluation",
        "diagram_generation",
    } <= agents_traced
    assert all(t.status == "ok" for t in result.trace)
    # Single trace id across the run.
    assert len({t.trace_id for t in result.trace}) == 1


async def test_workflow_graph_renders(coordinator, example_text):
    result = await coordinator.analyze(example_text)
    rf = result.workflow.to_reactflow()
    assert rf["nodes"] and rf["edges"]
    jg = result.workflow.to_json_graph()
    assert jg["graph"]["nodes"]
