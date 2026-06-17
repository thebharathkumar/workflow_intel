import { Link, useParams } from "react-router-dom";

import { exportUrl } from "../lib/api";
import { useAnalysis } from "../lib/useAnalysis";
import { ResultTabs } from "../components/Layout";
import { Badge, Card, List, Pills, ScoreBar, Section, Spinner, Stat } from "../components/ui";

export function Results() {
  const { id } = useParams();
  const { result, error, loading } = useAnalysis(id);

  if (loading) return <Spinner label="Loading analysis…" />;
  if (error || !result) return <p className="text-rose-400">{error ?? "Not found"}</p>;

  const r = result;
  const hours = r.bottlenecks.reduce((a, b) => a + b.annual_hours_saved, 0);

  return (
    <div>
      <ResultTabs id={r.id} />

      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white">Results Dashboard</h1>
          <p className="text-sm text-slate-400">
            <Badge tone="neutral">engine: {r.engine}</Badge>{" "}
            {r.model && <Badge tone="neutral">{r.model}</Badge>}{" "}
            <span className="text-slate-500">· {r.id}</span>
          </p>
        </div>
        <div className="flex gap-2">
          <a
            href={exportUrl(r.id, "json")}
            className="rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-200 hover:bg-slate-800"
          >
            Export JSON
          </a>
          <a
            href={exportUrl(r.id, "yaml")}
            className="rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-200 hover:bg-slate-800"
          >
            Export YAML
          </a>
          <Link
            to={`/results/${r.id}/canvas`}
            className="rounded-lg bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-500"
          >
            Open Canvas →
          </Link>
        </div>
      </div>

      <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        <Stat label="Steps" value={r.workflow.steps.length} />
        <Stat label="Bottlenecks" value={r.bottlenecks.length} />
        <Stat label="Agents" value={r.agents.length} />
        <Stat label="Integrations" value={r.integrations.length} />
        <Stat label="Risks" value={r.risks.length} />
        <Stat label="Hrs/yr saved" value={Math.round(hours)} hint="estimated" />
      </div>

      <Section title="Process Intelligence" subtitle={r.process_report.business_objective}>
        <Card>
          <p className="text-slate-200">{r.process_report.summary}</p>
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Field label="Participants" items={r.process_report.participants} />
            <Field label="Systems" items={r.process_report.systems} />
            <Field label="Inputs" items={r.process_report.inputs} />
            <Field label="Outputs" items={r.process_report.outputs} />
          </div>
          {r.process_report.risk_areas.length > 0 && (
            <div className="mt-4">
              <div className="mb-1 text-xs uppercase tracking-wide text-slate-500">Risk areas</div>
              <List items={r.process_report.risk_areas} />
            </div>
          )}
        </Card>
      </Section>

      <Section title="Bottlenecks & Opportunities" subtitle={`${r.bottlenecks.length} detected`}>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {r.bottlenecks
            .slice()
            .sort((a, b) => b.impact_score - a.impact_score)
            .map((b) => (
              <Card key={b.id}>
                <div className="mb-2 flex items-start justify-between gap-2">
                  <h3 className="font-semibold text-slate-100">{b.title}</h3>
                  <Badge tone={b.type}>{b.type.replace("_", " ")}</Badge>
                </div>
                <p className="text-sm text-slate-400">{b.description}</p>
                <div className="mt-3 grid grid-cols-3 gap-3">
                  <ScoreBar label="Impact" value={b.impact_score} />
                  <ScoreBar label="Complexity" value={b.complexity_score} />
                  <ScoreBar label="Confidence" value={b.confidence_score} />
                </div>
                <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
                  <span>
                    ROI: <span className="text-slate-200">{b.estimated_roi}</span>
                  </span>
                  <span>~{Math.round(b.annual_hours_saved)} hrs/yr</span>
                </div>
                <p className="mt-2 text-xs text-brand-300">{b.recommendation}</p>
              </Card>
            ))}
        </div>
      </Section>

      <Section title="Automation Blueprint" subtitle="Per-step type, platform & reasoning">
        <Card className="overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-800 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="p-3">Step</th>
                <th className="p-3">Type</th>
                <th className="p-3">Platform</th>
                <th className="p-3">Reasoning</th>
              </tr>
            </thead>
            <tbody>
              {r.automations.map((a) => (
                <tr key={a.step_id} className="border-b border-slate-800/60 align-top">
                  <td className="p-3 text-slate-200">{a.step_name}</td>
                  <td className="p-3">
                    <Badge tone="neutral">{a.automation_type.replace("_", " ")}</Badge>
                  </td>
                  <td className="p-3">
                    <span className="font-medium text-brand-300">{a.suggested_platform}</span>
                    {a.alternative_platforms.length > 0 && (
                      <div className="text-[11px] text-slate-500">
                        alt: {a.alternative_platforms.join(", ")}
                      </div>
                    )}
                  </td>
                  <td className="p-3 text-xs text-slate-400">{a.reasoning}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </Section>

      {r.agents.length > 0 && (
        <Section title="Agent Architecture" subtitle={`${r.agents.length} agent(s) designed`}>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {r.agents.map((a) => (
              <Card key={a.id}>
                <h3 className="font-semibold text-brand-300">{a.name}</h3>
                <p className="mt-1 text-sm text-slate-400">{a.purpose}</p>
                <div className="mt-3 space-y-3 text-sm">
                  <Block label="Responsibilities" items={a.responsibilities} />
                  <Block label="Tools" items={a.tools} />
                  <Block label="Escalation" items={a.escalation_rules} />
                  <Block label="HITL" items={a.hitl_rules} />
                  <Block label="Failure modes" items={a.failure_modes} />
                  <div>
                    <div className="text-xs uppercase tracking-wide text-slate-500">Recovery</div>
                    <p className="text-slate-300">{a.recovery_strategy}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </Section>
      )}

      <Section title="Enterprise Integrations" subtitle={`${r.integrations.length} system(s)`}>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {r.integrations.map((i) => (
            <Card key={i.system}>
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-slate-100">{i.system}</h3>
                <Badge tone="neutral">{i.direction}</Badge>
              </div>
              <div className="mt-1 text-xs text-slate-500">
                {i.category}
                {i.vendor ? ` · ${i.vendor}` : ""}
              </div>
              <div className="mt-3 space-y-2 text-xs">
                <KV label="Auth" value={i.auth_methods.join(", ")} />
                <KV label="Events" value={i.event_triggers.join(", ") || "—"} />
                <KV label="Webhooks" value={i.webhooks.join(", ") || "—"} />
                {i.mcp_opportunity && (
                  <div className="rounded-md bg-violet-500/10 p-2 text-violet-300">
                    MCP: {i.mcp_opportunity}
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      </Section>

      <Section title="Evaluation Framework" subtitle="Measurable KPIs">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {r.evaluation.map((e) => (
            <Card key={e.id}>
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-slate-100">{e.name}</h3>
                <Badge tone="neutral">{e.target}</Badge>
              </div>
              <p className="mt-1 text-sm text-slate-400">{e.description}</p>
              <div className="mt-2 text-xs text-slate-400">
                <span className="text-slate-500">Metric:</span> {e.metric}
              </div>
              <div className="text-xs text-emerald-300">KPI: {e.kpi_target}</div>
            </Card>
          ))}
        </div>
      </Section>
    </div>
  );
}

function Field({ label, items }: { label: string; items: string[] }) {
  return (
    <div>
      <div className="mb-1 text-xs uppercase tracking-wide text-slate-500">{label}</div>
      {items.length ? <Pills items={items} /> : <span className="text-sm text-slate-600">—</span>}
    </div>
  );
}

function Block({ label, items }: { label: string; items: string[] }) {
  if (!items.length) return null;
  return (
    <div>
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <List items={items} />
    </div>
  );
}

function KV({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span className="text-slate-500">{label}:</span> <span className="text-slate-300">{value}</span>
    </div>
  );
}
