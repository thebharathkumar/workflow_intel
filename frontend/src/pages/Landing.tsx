import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getMeta } from "../lib/api";
import type { Meta } from "../lib/types";
import { Card } from "../components/ui";

const OUTPUTS = [
  ["Process Intelligence", "Summary, objective, participants, systems, dependencies, risk areas"],
  ["Workflow Graph (DAG)", "Steps, actors, systems, decisions — Mermaid, React Flow & JSON"],
  ["Bottleneck Detection", "Human / system / AI-candidate, each scored for impact, ROI & complexity"],
  ["Automation Blueprint", "Per-step type + platform (n8n, Temporal, LangGraph…) with reasoning"],
  ["Agent Architecture", "Responsibilities, tools, memory, escalation, HITL, failure & recovery"],
  ["Integration Layer", "APIs, auth, events, webhooks, and MCP opportunities per system"],
  ["Governance Analysis", "Every step classified across four automation-governance tiers"],
  ["AI Risk Assessment", "Hallucination, leakage, compliance, PII, financial, operational"],
  ["Observability Framework", "Traces, metrics, dashboards (OTel, LangSmith, Arize, Grafana)"],
  ["Evaluation Framework", "Workflow, agent, routing, tool-selection & escalation KPIs"],
  ["Architecture Diagrams", "System, agent, data-flow, sequence & integration (Mermaid)"],
  ["Spec Export", "Downloadable JSON / YAML automation specification"],
];

export function Landing() {
  const [meta, setMeta] = useState<Meta | null>(null);
  useEffect(() => {
    getMeta().then(setMeta).catch(() => undefined);
  }, []);

  return (
    <div>
      <section className="mb-12 text-center">
        <div className="mx-auto mb-4 inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900 px-3 py-1 text-xs text-slate-400">
          <span className="h-2 w-2 rounded-full bg-emerald-400" />
          {meta
            ? `engine: ${meta.default_engine}${meta.llm_available ? ` · ${meta.llm_model}` : ""} · v${meta.version}`
            : "loading capabilities…"}
        </div>
        <h1 className="mx-auto max-w-3xl text-4xl font-bold tracking-tight text-white sm:text-5xl">
          Turn a paragraph of business process into an{" "}
          <span className="text-brand-400">AI automation blueprint</span>.
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-slate-400">
          Workflow Intel analyzes a plain-English workflow and produces a governed, observable,
          agent-ready automation architecture — not a chatbot answer, a multi-agent analysis with a
          deterministic core and an optional Claude layer.
        </p>
        <div className="mt-8 flex justify-center gap-3">
          <Link
            to="/analyze"
            className="rounded-lg bg-brand-600 px-5 py-2.5 font-medium text-white hover:bg-brand-500"
          >
            Analyze a workflow →
          </Link>
          <a
            href="/docs"
            className="rounded-lg border border-slate-700 px-5 py-2.5 font-medium text-slate-200 hover:bg-slate-800"
          >
            API docs
          </a>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {OUTPUTS.map(([title, desc]) => (
          <Card key={title}>
            <h3 className="font-semibold text-slate-100">{title}</h3>
            <p className="mt-1 text-sm text-slate-400">{desc}</p>
          </Card>
        ))}
      </section>

      {meta && (
        <section className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Card>
            <h3 className="mb-2 font-semibold text-slate-100">
              {meta.supported_systems.length} enterprise systems recognized
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {meta.supported_systems.slice(0, 24).map((s) => (
                <span key={s} className="rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-300">
                  {s}
                </span>
              ))}
            </div>
          </Card>
          <Card>
            <h3 className="mb-2 font-semibold text-slate-100">Automation platforms evaluated</h3>
            <div className="flex flex-wrap gap-1.5">
              {meta.automation_platforms.map((p) => (
                <span key={p} className="rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-300">
                  {p}
                </span>
              ))}
            </div>
            <p className="mt-3 text-xs text-slate-500">
              LangGraph available: {String(meta.langgraph_available)} · OTel:{" "}
              {String(meta.otel_enabled)}
            </p>
          </Card>
        </section>
      )}
    </div>
  );
}
