"""Base agent: a traced, async unit of analysis."""

from __future__ import annotations

from workflow_intel.agents.state import PipelineState
from workflow_intel.observability.tracing import Span, trace_agent


class Agent:
    """All specialist agents subclass this. ``run`` wraps ``_execute`` in a recorded span."""

    name: str = "agent"

    async def run(self, state: PipelineState) -> PipelineState:
        async with trace_agent(state.recorder, self.name) as span:
            await self._execute(state, span)
        return state

    async def _execute(self, state: PipelineState, span: Span) -> None:  # pragma: no cover
        raise NotImplementedError
