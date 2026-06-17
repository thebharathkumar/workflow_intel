import { useParams } from "react-router-dom";

import { useAnalysis } from "../lib/useAnalysis";
import { ResultTabs } from "../components/Layout";
import { Badge, Card, Section, Spinner, Stat } from "../components/ui";

export function Observability() {
  const { id } = useParams();
  const { result, error, loading } = useAnalysis(id);

  if (loading) return <Spinner label="Loading observability…" />;
  if (error || !result) return <p className="text-rose-400">{error ?? "Not found"}</p>;

  const o = result.observability;
  const totalLatency = result.trace.reduce((a, t) => a + t.latency_ms, 0);
  const totalCost = result.trace.reduce((a, t) => a + t.cost_usd_estimate, 0);
  const totalTokens = result.trace.reduce((a, t) => a + t.token_estimate, 0);

  return (
    <div>
      <ResultTabs id={result.id} />
      <h1 className="mb-1 text-2xl font-bold text-white">Observability</h1>
      <p className="mb-6 text-sm text-slate-400">
        Captured traces from this run plus the recommended telemetry, dashboards, and SLOs.
      </p>

      <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Spans captured" value={result.trace.length} />
        <Stat label="Pipeline latency" value={`${totalLatency.toFixed(1)} ms`} />
        <Stat label="Tokens" value={totalTokens} hint="0 in deterministic mode" />
        <Stat label="Est. cost" value={`$${totalCost.toFixed(4)}`} />
      </div>

      <Section title="Captured agent traces" subtitle="In-memory span recorder (mirrors OTel export)">
        <Card className="overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-800 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="p-3">Agent</th>
                <th className="p-3">Status</th>
                <th className="p-3">Latency</th>
                <th className="p-3">Tokens</th>
                <th className="p-3">Cost</th>
                <th className="p-3">Attributes</th>
              </tr>
            </thead>
            <tbody>
              {result.trace.map((t) => (
                <tr key={t.span_id} className="border-b border-slate-800/60 align-top">
                  <td className="p-3 font-mono text-xs text-slate-200">{t.agent}</td>
                  <td className="p-3">
                    <Badge tone={t.status === "ok" ? "safe_for_full_automation" : "critical"}>
                      {t.status}
                    </Badge>
                  </td>
                  <td className="p-3 text-slate-300">{t.latency_ms.toFixed(2)} ms</td>
                  <td className="p-3 text-slate-300">{t.token_estimate}</td>
                  <td className="p-3 text-slate-300">${t.cost_usd_estimate.toFixed(4)}</td>
                  <td className="p-3 text-[11px] text-slate-500">
                    {Object.entries(t.attributes)
                      .map(([k, v]) => `${k}=${String(v)}`)
                      .join(" · ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </Section>

      <Section title="Telemetry signals">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {o.signals.map((s) => (
            <Card key={s.name}>
              <div className="flex items-center justify-between">
                <span className="font-mono text-sm text-brand-300">{s.name}</span>
                <Badge tone="neutral">{s.telemetry_type}</Badge>
              </div>
              <p className="mt-1 text-xs text-slate-400">{s.description}</p>
              {s.otel_instrument && (
                <p className="mt-1 text-[11px] text-slate-600">otel: {s.otel_instrument}</p>
              )}
            </Card>
          ))}
        </div>
      </Section>

      <Section title="Dashboards">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {o.dashboards.map((d) => (
            <Card key={d.name}>
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-slate-100">{d.name}</h3>
                <span className="text-[11px] text-slate-500">{d.tool}</span>
              </div>
              <ul className="mt-2 space-y-1 text-xs text-slate-400">
                {d.panels.map((p) => (
                  <li key={p}>• {p}</li>
                ))}
              </ul>
            </Card>
          ))}
        </div>
      </Section>

      <Section title="Tooling & SLOs">
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Card>
            <h3 className="mb-2 font-semibold text-slate-100">Recommended tools</h3>
            <ul className="space-y-2 text-sm">
              {o.tools.map((t) => (
                <li key={t.tool}>
                  <span className="font-medium text-slate-200">{t.tool}</span>{" "}
                  <span className="text-slate-400">— {t.purpose}</span>
                </li>
              ))}
            </ul>
          </Card>
          <Card>
            <h3 className="mb-2 font-semibold text-slate-100">Service-level objectives</h3>
            <ul className="space-y-2 text-sm">
              {o.slos.map((s) => (
                <li key={s.objective} className="flex justify-between">
                  <span className="text-slate-300">{s.objective}</span>
                  <span className="text-emerald-300">{s.target}</span>
                </li>
              ))}
            </ul>
          </Card>
        </div>
      </Section>
    </div>
  );
}
