"""Integration Agent — API, auth, event, webhook, and MCP plan per system."""

from __future__ import annotations

from workflow_intel.agents.base import Agent
from workflow_intel.agents.state import PipelineState
from workflow_intel.domain.enums import StepType
from workflow_intel.domain.models import Integration
from workflow_intel.knowledge.systems import SYSTEM_CATALOG
from workflow_intel.observability.tracing import Span


class IntegrationAgent(Agent):
    name = "integration"

    async def _execute(self, state: PipelineState, span: Span) -> None:
        wf = state.workflow
        assert wf is not None
        integrations: list[Integration] = []

        for system in wf.systems:
            meta = SYSTEM_CATALOG.get(system.name, {})
            direction = self._direction(system.name, state)
            integrations.append(
                Integration(
                    system=system.name,
                    category=system.category,
                    vendor=system.vendor,
                    direction=direction,
                    api_requirements=[
                        f"REST/Bulk API access to: {', '.join(meta.get('data_objects', ['core objects']))}",
                        "Rate-limit-aware client with retry/backoff",
                        "Least-privilege scopes for the objects above",
                    ],
                    auth_methods=meta.get("auth", ["OAuth 2.0"]),
                    event_triggers=meta.get("events", []),
                    webhooks=meta.get("webhooks", []),
                    data_objects=meta.get("data_objects", []),
                    mcp_opportunity=meta.get("mcp"),
                )
            )

        state.integrations = integrations
        span.set(
            integrations=len(integrations),
            with_webhooks=sum(1 for i in integrations if i.webhooks),
            mcp_candidates=sum(1 for i in integrations if i.mcp_opportunity),
        )

    def _direction(self, system_name: str, state: PipelineState) -> str:
        wf = state.workflow
        assert wf is not None
        writes = reads = False
        for step in wf.steps:
            if system_name not in step.systems:
                continue
            if step.type in (StepType.DATA_ENTRY, StepType.STORAGE, StepType.INTEGRATION):
                writes = True
            if step.type in (StepType.REVIEW, StepType.DECISION):
                reads = True
            if step.type == StepType.NOTIFICATION:
                writes = True
        if writes and reads:
            return "bidirectional"
        if writes:
            return "write"
        if reads:
            return "read"
        return "bidirectional"
