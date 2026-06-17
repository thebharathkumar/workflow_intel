"""LangGraph adapter.

Builds a ``StateGraph`` whose nodes delegate to the Coordinator's *same* agent instances, so the
pipeline executes as a true LangGraph state machine when the optional dependency is installed.
The DAG mirrors ``Coordinator._run`` exactly. If LangGraph is not installed, importing this module
raises and the Coordinator falls back to direct execution.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

from langgraph.graph import END, START, StateGraph  # noqa: F401  (import-guarded by caller)

from workflow_intel.agents.state import PipelineState

if TYPE_CHECKING:
    from workflow_intel.agents.coordinator import Coordinator


class GraphState(TypedDict):
    state: PipelineState


def build_graph(coordinator: Coordinator) -> Any:
    """Construct and compile the LangGraph ``StateGraph`` for the pipeline."""

    def _node(agent):
        async def run(gs: GraphState) -> dict:
            await agent.run(gs["state"])
            return {}

        return run

    g = StateGraph(GraphState)
    g.add_node("extraction", _node(coordinator.extraction))
    g.add_node("intelligence", _node(coordinator.intelligence))
    g.add_node("automation", _node(coordinator.automation))
    g.add_node("integration", _node(coordinator.integration))
    g.add_node("governance", _node(coordinator.governance))
    g.add_node("observability", _node(coordinator.observability))
    g.add_node("evaluation", _node(coordinator.evaluation))
    g.add_node("diagram", _node(coordinator.diagram))

    g.add_edge(START, "extraction")
    g.add_edge("extraction", "intelligence")
    g.add_edge("intelligence", "automation")
    g.add_edge("intelligence", "integration")
    g.add_edge("automation", "governance")
    g.add_edge("integration", "governance")
    g.add_edge("governance", "observability")
    g.add_edge("governance", "evaluation")
    g.add_edge("observability", "diagram")
    g.add_edge("evaluation", "diagram")
    g.add_edge("diagram", END)
    return g.compile()


async def run_with_langgraph(coordinator: Coordinator, state: PipelineState) -> None:
    graph = build_graph(coordinator)
    await graph.ainvoke({"state": state})
