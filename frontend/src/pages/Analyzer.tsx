import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { analyze, getMeta } from "../lib/api";
import type { Meta } from "../lib/types";
import { Card, Spinner } from "../components/ui";

const EXAMPLE =
  "Sales emails contracts to Legal. Legal reviews and sends comments back. " +
  "Sales updates Salesforce. Finance receives a Slack notification. " +
  "Contracts are stored in SharePoint.";

const EXAMPLES = [
  EXAMPLE,
  "A customer submits a support ticket in Zendesk. An agent triages and routes it to the right team. " +
    "Engineering investigates in Jira. The customer is updated by email. Resolved tickets are summarized weekly.",
  "Procurement receives an invoice by email. Finance manually enters it into SAP and validates the PO. " +
    "A manager approves payment. The vendor is notified and the invoice is archived in SharePoint.",
];

export function Analyzer() {
  const navigate = useNavigate();
  const [text, setText] = useState(EXAMPLE);
  const [useLlm, setUseLlm] = useState(false);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMeta().then(setMeta).catch(() => undefined);
  }, []);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      const result = await analyze(text, useLlm);
      navigate(`/results/${result.id}`);
    } catch (e) {
      setError(String(e));
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-1 text-2xl font-bold text-white">Analyze a workflow</h1>
      <p className="mb-6 text-slate-400">
        Describe a business process in plain English. The pipeline extracts the workflow, scores
        bottlenecks, designs agents, and assesses governance & risk.
      </p>

      <Card>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={8}
          className="w-full resize-y rounded-lg border border-slate-700 bg-slate-950 p-3 text-sm text-slate-100 outline-none focus:border-brand-500"
          placeholder="e.g. Sales emails contracts to Legal…"
        />
        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
          <span className="text-slate-500">Try:</span>
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              onClick={() => setText(ex)}
              className="rounded-md border border-slate-700 px-2 py-1 text-slate-300 hover:bg-slate-800"
            >
              Example {i + 1}
            </button>
          ))}
        </div>

        <div className="mt-4 flex items-center justify-between">
          <label
            className={`flex items-center gap-2 text-sm ${
              meta?.llm_available ? "text-slate-300" : "text-slate-600"
            }`}
            title={meta?.llm_available ? "" : "Server has no LLM configured; deterministic engine is used."}
          >
            <input
              type="checkbox"
              disabled={!meta?.llm_available}
              checked={useLlm}
              onChange={(e) => setUseLlm(e.target.checked)}
            />
            Use LLM extraction {meta && !meta.llm_available && "(unavailable)"}
          </label>
          <button
            onClick={run}
            disabled={loading || text.trim().length < 10}
            className="rounded-lg bg-brand-600 px-5 py-2 font-medium text-white hover:bg-brand-500 disabled:opacity-40"
          >
            {loading ? "Analyzing…" : "Analyze →"}
          </button>
        </div>
        {loading && (
          <div className="mt-4">
            <Spinner label="Running 8-agent pipeline…" />
          </div>
        )}
        {error && <p className="mt-4 text-sm text-rose-400">{error}</p>}
      </Card>
    </div>
  );
}
