import { useParams } from "react-router-dom";

import { useAnalysis } from "../lib/useAnalysis";
import { ResultTabs } from "../components/Layout";
import { Badge, Card, List, Section, Spinner } from "../components/ui";

export function Governance() {
  const { id } = useParams();
  const { result, error, loading } = useAnalysis(id);

  if (loading) return <Spinner label="Loading governance…" />;
  if (error || !result) return <p className="text-rose-400">{error ?? "Not found"}</p>;

  const counts = result.governance.reduce<Record<string, number>>((acc, g) => {
    acc[g.classification] = (acc[g.classification] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <div>
      <ResultTabs id={result.id} />
      <h1 className="mb-1 text-2xl font-bold text-white">Governance & AI Risk</h1>
      <p className="mb-6 text-sm text-slate-400">
        Every step is classified into an automation-governance tier, with an independent AI risk
        register.
      </p>

      <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        {Object.entries(counts).map(([cls, n]) => (
          <Card key={cls} className="text-center">
            <div className="text-2xl font-bold text-white">{n}</div>
            <div className="mt-1">
              <Badge tone={cls}>{cls.replace(/_/g, " ")}</Badge>
            </div>
          </Card>
        ))}
      </div>

      <Section title="Step classification">
        <Card className="overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-800 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="p-3">Step</th>
                <th className="p-3">Classification</th>
                <th className="p-3">Rationale</th>
                <th className="p-3">Controls</th>
              </tr>
            </thead>
            <tbody>
              {result.governance.map((g) => (
                <tr key={g.step_id} className="border-b border-slate-800/60 align-top">
                  <td className="p-3 text-slate-200">{g.step_name}</td>
                  <td className="p-3">
                    <Badge tone={g.classification}>{g.classification.replace(/_/g, " ")}</Badge>
                  </td>
                  <td className="p-3 text-xs text-slate-400">{g.rationale}</td>
                  <td className="p-3 text-xs text-slate-400">{g.controls.join("; ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </Section>

      <Section title="AI Risk Register" subtitle={`${result.risks.length} risks across 6 categories`}>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {result.risks
            .slice()
            .sort((a, b) => b.risk_score - a.risk_score)
            .map((risk) => (
              <Card key={risk.id}>
                <div className="mb-2 flex items-start justify-between gap-2">
                  <div>
                    <div className="text-xs uppercase tracking-wide text-slate-500">
                      {risk.category}
                    </div>
                    <h3 className="font-semibold text-slate-100">{risk.title}</h3>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <Badge tone={risk.severity}>{risk.severity}</Badge>
                    <span className="text-[11px] text-slate-500">score {risk.risk_score}/20</span>
                  </div>
                </div>
                <p className="text-sm text-slate-400">{risk.description}</p>
                <div className="mt-2 text-xs text-slate-500">
                  Likelihood: <span className="text-slate-300">{risk.likelihood}</span> · Owner:{" "}
                  {risk.owner}
                </div>
                <div className="mt-2 text-xs">
                  <span className="text-slate-500">Mitigation:</span>{" "}
                  <span className="text-emerald-300">{risk.mitigation}</span>
                </div>
              </Card>
            ))}
        </div>
      </Section>

      <Section title="Controls summary">
        <Card>
          <List
            items={Array.from(
              new Set(result.governance.flatMap((g) => g.controls)),
            )}
          />
        </Card>
      </Section>
    </div>
  );
}
