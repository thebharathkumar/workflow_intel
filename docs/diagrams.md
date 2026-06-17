# Architecture Diagrams

The Diagram Generation Agent emits five Mermaid diagrams **per analysis** (system, agent,
data-flow, sequence, integration) plus the workflow DAG — fetch them at
`GET /analyses/{id}/diagram/{kind}` or view them on the Architecture Canvas. The system/agent/
data-flow/sequence templates below are the static platform views; the integration and workflow
diagrams are fully data-driven from each result.

## System architecture
```mermaid
flowchart LR
    UI["React SPA"] --> API["FastAPI + middleware"]
    API --> COORD["Coordinator / LangGraph"]
    COORD --> AG["8 Specialist Agents"]
    AG --> KB[("Knowledge Catalogs")]
    AG -. optional .-> LLM[["claude-opus-4-8"]]
    COORD --> REPO[("Repository")]
    API -. spans .-> OTEL[["OTel Collector"]]
    API --> UI
```

## Agent architecture
```mermaid
flowchart TD
    IN(["workflow text"]) --> EX[Workflow Extraction]
    EX --> PI[Process Intelligence]
    EX --> IN2[Integration]
    PI --> AA[Automation Architect]
    AA --> GV[Governance + Risk]
    PI --> SYN{{Coordinator synthesize}}
    AA --> SYN
    GV --> SYN
    IN2 --> SYN
    SYN --> OB[Observability]
    SYN --> EV[Evaluation]
    OB --> DG[Diagram Generation]
    EV --> DG
    DG --> OUT(["AnalysisResult"])
```

## Data flow
```mermaid
flowchart LR
    T["Raw description"] --> X["Extraction → WorkflowGraph"]
    X --> A["Analysis: bottlenecks · automations · governance · integrations"]
    A --> S["Synthesis: observability · evaluation · diagrams"]
    S --> R[("AnalysisResult (persisted)")]
    R --> E["Export JSON / YAML"]
    R --> V["Dashboards / Canvas"]
    R --> TR["Captured agent traces"]
```

## Sequence
```mermaid
sequenceDiagram
    actor User
    participant API as FastAPI
    participant C as Coordinator
    participant EX as Extraction
    participant AN as Analysis Agents
    participant DB as Repository
    User->>API: POST /analyze (description)
    API->>C: run pipeline
    C->>EX: extract workflow
    EX-->>C: WorkflowGraph
    C->>AN: fan-out (PI, automation, governance, integration)
    AN-->>C: analysis outputs
    C->>C: synthesize (obs, eval, diagrams)
    C->>DB: persist AnalysisResult + traces
    API-->>User: AnalysisResult
```

## Integration (example — generated per analysis)
```mermaid
flowchart LR
    WI(["Workflow Intel"])
    NSalesforce["Salesforce<br/>CRM"]
    WI <-->|OAuth 2.0 (JWT bearer)| NSalesforce
    NSlack["Slack<br/>Messaging"]
    WI <-->|OAuth 2.0 (bot token)| NSlack
    NSharePoint["SharePoint<br/>Document Management"]
    WI <-->|OAuth 2.0 (Microsoft Entra ID)| NSharePoint
```
