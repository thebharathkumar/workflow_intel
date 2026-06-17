import { useEffect, useState } from "react";

import { getAnalysis } from "./api";
import type { AnalysisResult } from "./types";

export function useAnalysis(id: string | undefined) {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setLoading(true);
    getAnalysis(id)
      .then((r) => !cancelled && setResult(r))
      .catch((e) => !cancelled && setError(String(e)))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [id]);

  return { result, error, loading };
}
