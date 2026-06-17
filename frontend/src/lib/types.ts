// Mirrors the backend Pydantic domain model (workflow_intel/domain/models.py).

export type EngineKind = "deterministic" | "llm" | "hybrid";
export type BottleneckType = "human" | "system" | "ai_candidate";

export interface WorkflowStep {
  id: string;
  name: string;
  description: string;
  type: string;
  actor: string | null;
  systems: string[];
  inputs: string[];
  outputs: string[];
  order: number;
  is_manual: boolean;
  is_external_comm: boolean;
  is_repetitive: boolean;
  touches_pii: boolean;
  financial_impact: boolean;
  irreversible: boolean;
}

export interface Actor {
  name: string;
  type: string;
  role: string | null;
}
export interface SystemRef {
  name: string;
  category: string;
  vendor: string | null;
}
export interface WorkflowNode {
  id: string;
  label: string;
  type: string;
  lane: string | null;
  position: { x: number; y: number };
  data: Record<string, unknown>;
}
export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  label: string | null;
}
export interface WorkflowGraph {
  steps: WorkflowStep[];
  actors: Actor[];
  systems: SystemRef[];
  handoffs: unknown[];
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

export interface ProcessReport {
  summary: string;
  business_objective: string;
  participants: string[];
  systems: string[];
  inputs: string[];
  outputs: string[];
  dependencies: string[];
  risk_areas: string[];
}

export interface Bottleneck {
  id: string;
  type: BottleneckType;
  title: string;
  description: string;
  step_ids: string[];
  impact_score: number;
  complexity_score: number;
  confidence_score: number;
  estimated_roi: string;
  annual_hours_saved: number;
  ai_capability: string | null;
  recommendation: string;
}

export interface AutomationRecommendation {
  step_id: string;
  step_name: string;
  automation_type: string;
  suggested_platform: string;
  alternative_platforms: string[];
  reasoning: string;
  confidence_score: number;
  prerequisites: string[];
}

export interface AgentDesign {
  id: string;
  name: string;
  purpose: string;
  responsibilities: string[];
  inputs: string[];
  outputs: string[];
  tools: string[];
  memory_requirements: string[];
  escalation_rules: string[];
  hitl_rules: string[];
  evaluation_metrics: string[];
  failure_modes: string[];
  recovery_strategy: string;
  guardrails: string[];
}

export interface Integration {
  system: string;
  category: string;
  vendor: string | null;
  direction: string;
  api_requirements: string[];
  auth_methods: string[];
  event_triggers: string[];
  webhooks: string[];
  data_objects: string[];
  mcp_opportunity: string | null;
}

export interface GovernanceClassification {
  step_id: string;
  step_name: string;
  classification: string;
  rationale: string;
  controls: string[];
}

export interface RiskItem {
  id: string;
  category: string;
  title: string;
  description: string;
  severity: string;
  likelihood: string;
  mitigation: string;
  owner: string;
  risk_score: number;
}

export interface ObservabilitySignal {
  name: string;
  telemetry_type: string;
  description: string;
  otel_instrument: string | null;
  unit: string | null;
}
export interface Dashboard {
  name: string;
  tool: string;
  panels: string[];
}
export interface ObservabilitySpec {
  signals: ObservabilitySignal[];
  tools: { tool: string; purpose: string }[];
  dashboards: Dashboard[];
  slos: { objective: string; target: string }[];
}

export interface EvaluationSpec {
  id: string;
  name: string;
  target: string;
  description: string;
  metric: string;
  kpi_target: string;
  method: string;
  dataset: string;
  cadence: string;
}

export interface AgentTrace {
  trace_id: string;
  span_id: string;
  parent_span_id: string | null;
  agent: string;
  status: string;
  started_at: string;
  latency_ms: number;
  token_estimate: number;
  cost_usd_estimate: number;
  error: string | null;
  attributes: Record<string, unknown>;
}

export interface AnalysisResult {
  id: string;
  created_at: string;
  source_text: string;
  engine: EngineKind;
  model: string | null;
  process_report: ProcessReport;
  workflow: WorkflowGraph;
  bottlenecks: Bottleneck[];
  automations: AutomationRecommendation[];
  agents: AgentDesign[];
  integrations: Integration[];
  governance: GovernanceClassification[];
  risks: RiskItem[];
  observability: ObservabilitySpec;
  evaluation: EvaluationSpec[];
  diagrams: Record<string, string>;
  trace: AgentTrace[];
}

export interface AnalysisSummary {
  id: string;
  created_at: string;
  engine: EngineKind;
  title: string;
  step_count: number;
  actor_count: number;
  system_count: number;
  bottleneck_count: number;
  agent_count: number;
  risk_count: number;
}

export interface Meta {
  app_name: string;
  version: string;
  environment: string;
  default_engine: string;
  llm_available: boolean;
  llm_model: string;
  langgraph_available: boolean;
  otel_enabled: boolean;
  supported_systems: string[];
  automation_platforms: string[];
}

export interface TraceResponse {
  analysis_id: string;
  trace_id: string | null;
  span_count: number;
  total_latency_ms: number;
  total_cost_usd_estimate: number;
  spans: AgentTrace[];
}
