import { useState } from "react";
import { useParams } from "react-router-dom";

import { useAnalysis } from "../lib/useAnalysis";
import { ResultTabs } from "../components/Layout";
import { MermaidDiagram } from "../components/MermaidDiagram";
import { WorkflowCanvas } from "../components/WorkflowCanvas";
import { Card, Spinner } from "../components/ui";

const DIAGRAMS = [
  ["workflow", "Workflow"],
  ["system", "System"],
  ["agent", "Agent"],
  ["data_flow", "Data Flow"],
  ["sequence", "Sequence"],
  ["integration", "Integration"],
];

export function Canvas() {
  const { id } = useParams();
  const { result, error, loading } = useAnalysis(id);
  const [diagram, setDiagram] = useState("system");

  if (loading) return <Spinner label="Loading canvas…" />;
  if (error || !result) return <p className="text-rose-400">{error ?? "Not found"}</p>;

  return (
    <div>
      <ResultTabs id={result.id} />
      <h1 className="mb-1 text-2xl font-bold text-white">Architecture Canvas</h1>
      <p className="mb-6 text-sm text-slate-400">
        Interactive workflow DAG plus generated Mermaid architecture diagrams.
      </p>

      <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-400">
        Interactive workflow graph
      </h2>
      <WorkflowCanvas graph={result.workflow} />

      <div className="mt-8">
        <div className="mb-3 flex flex-wrap gap-2">
          {DIAGRAMS.map(([key, label]) => (
            <button
              key={key}
              onClick={() => setDiagram(key)}
              className={`rounded-md px-3 py-1.5 text-sm ${
                diagram === key
                  ? "bg-brand-600 text-white"
                  : "border border-slate-700 text-slate-300 hover:bg-slate-800"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
        <Card>
          {result.diagrams[diagram] ? (
            <MermaidDiagram chart={result.diagrams[diagram]} />
          ) : (
            <p className="text-slate-500">No diagram.</p>
          )}
        </Card>
      </div>
    </div>
  );
}
