import type {
  AnalysisResult,
  AnalysisSummary,
  Meta,
  TraceResponse,
} from "./types";

const BASE = "/api/v1";

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export async function analyze(text: string, useLlm?: boolean): Promise<AnalysisResult> {
  const res = await fetch(`${BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, use_llm: useLlm ?? null }),
  });
  return json<AnalysisResult>(res);
}

export async function getAnalysis(id: string): Promise<AnalysisResult> {
  return json<AnalysisResult>(await fetch(`${BASE}/analyses/${id}`));
}

export async function listAnalyses(): Promise<AnalysisSummary[]> {
  return json<AnalysisSummary[]>(await fetch(`${BASE}/analyses`));
}

export async function getTraces(id: string): Promise<TraceResponse> {
  return json<TraceResponse>(await fetch(`${BASE}/analyses/${id}/traces`));
}

export async function getMeta(): Promise<Meta> {
  return json<Meta>(await fetch(`${BASE}/meta`));
}

export function exportUrl(id: string, format: "json" | "yaml"): string {
  return `${BASE}/analyses/${id}/export?format=${format}`;
}
