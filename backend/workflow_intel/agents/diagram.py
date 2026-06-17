"""Diagram Generation Agent — Mermaid for system, agent, data-flow, sequence, integration."""

from __future__ import annotations

from workflow_intel.agents.base import Agent
from workflow_intel.agents.state import PipelineState
from workflow_intel.observability.tracing import Span


def _san(text: str) -> str:
    return text.replace('"', "'").replace("[", "(").replace("]", ")").replace("\n", " ").strip()


class DiagramGenerationAgent(Agent):
    name = "diagram_generation"

    async def _execute(self, state: PipelineState, span: Span) -> None:
        wf = state.workflow
        assert wf is not None
        diagrams = {
            "workflow": wf.to_mermaid(),
            "system": self._system(),
            "agent": self._agent(state),
            "data_flow": self._data_flow(),
            "sequence": self._sequence(state),
            "integration": self._integration(state),
        }
        state.diagrams = diagrams
        span.set(diagrams=len(diagrams))

    def _system(self) -> str:
        return (
            "flowchart LR\n"
            '    UI["React SPA"] --> API["FastAPI + middleware"]\n'
            '    API --> COORD["Coordinator / LangGraph"]\n'
            '    COORD --> AG["8 Specialist Agents"]\n'
            '    AG --> KB[("Knowledge Catalogs")]\n'
            '    AG -. optional .-> LLM[["claude-opus-4-8"]]\n'
            '    COORD --> REPO[("Repository")]\n'
            '    API -. spans .-> OTEL[["OTel Collector"]]\n'
            "    API --> UI"
        )

    def _agent(self, state: PipelineState) -> str:
        lines = [
            "flowchart TD",
            '    IN(["workflow text"]) --> EX[Workflow Extraction]',
            "    EX --> PI[Process Intelligence]",
            "    EX --> IN2[Integration]",
            "    PI --> AA[Automation Architect]",
            "    AA --> GV[Governance + Risk]",
            "    PI --> SYN{{Coordinator synthesize}}",
            "    AA --> SYN",
            "    GV --> SYN",
            "    IN2 --> SYN",
            "    SYN --> OB[Observability]",
            "    SYN --> EV[Evaluation]",
            "    OB --> DG[Diagram Generation]",
            "    EV --> DG",
            '    DG --> OUT(["AnalysisResult"])',
        ]
        for design in state.agents:
            lines.append(f'    GV -. designs .-> {self._node_id(design.name)}(["{_san(design.name)}"])')
        return "\n".join(lines)

    def _data_flow(self) -> str:
        return (
            "flowchart LR\n"
            '    T["Raw description"] --> X["Extraction → WorkflowGraph"]\n'
            '    X --> A["Analysis: bottlenecks · automations · governance · integrations"]\n'
            '    A --> S["Synthesis: observability · evaluation · diagrams"]\n'
            '    S --> R[("AnalysisResult (persisted)")]\n'
            '    R --> E["Export JSON / YAML"]\n'
            '    R --> V["Dashboards / Canvas"]\n'
            '    R --> TR["Captured agent traces"]'
        )

    def _sequence(self, state: PipelineState) -> str:
        engine = state.engine.value
        return (
            "sequenceDiagram\n"
            "    actor User\n"
            "    participant API as FastAPI\n"
            "    participant C as Coordinator\n"
            "    participant EX as Extraction\n"
            "    participant AN as Analysis Agents\n"
            "    participant DB as Repository\n"
            "    User->>API: POST /analyze (description)\n"
            "    API->>C: run pipeline\n"
            "    C->>EX: extract workflow\n"
            f"    EX-->>C: WorkflowGraph ({engine})\n"
            "    C->>AN: fan-out (PI, automation, governance, integration)\n"
            "    AN-->>C: analysis outputs\n"
            "    C->>C: synthesize (obs, eval, diagrams)\n"
            "    C->>DB: persist AnalysisResult + traces\n"
            "    API-->>User: AnalysisResult"
        )

    def _integration(self, state: PipelineState) -> str:
        lines = ["flowchart LR", '    WI(["Workflow Intel"])']
        for integ in state.integrations:
            nid = self._node_id(integ.system)
            arrow = {"read": "-->", "write": "<--", "bidirectional": "<-->"}.get(integ.direction, "<-->")
            auth = integ.auth_methods[0] if integ.auth_methods else "OAuth 2.0"
            lines.append(f'    {nid}["{_san(integ.system)}<br/>{_san(integ.category)}"]')
            lines.append(f"    WI {arrow}|{_san(auth)}| {nid}")
        if not state.integrations:
            lines.append('    WI -.-> NONE["No external systems named"]')
        return "\n".join(lines)

    @staticmethod
    def _node_id(name: str) -> str:
        return "N" + "".join(c for c in name if c.isalnum())[:24]
