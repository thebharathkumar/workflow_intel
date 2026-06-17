import mermaid from "mermaid";
import { useEffect, useId, useRef, useState } from "react";

mermaid.initialize({ startOnLoad: false, theme: "dark", securityLevel: "loose" });

export function MermaidDiagram({ chart }: { chart: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const id = useId().replace(/:/g, "_");

  useEffect(() => {
    let cancelled = false;
    mermaid
      .render(`m_${id}`, chart)
      .then(({ svg }) => {
        if (!cancelled && ref.current) ref.current.innerHTML = svg;
      })
      .catch((e) => !cancelled && setError(String(e)));
    return () => {
      cancelled = true;
    };
  }, [chart, id]);

  if (error) {
    return <pre className="overflow-auto rounded-lg bg-slate-900 p-3 text-xs text-rose-300">{chart}</pre>;
  }
  return <div ref={ref} className="overflow-auto rounded-lg bg-slate-900/60 p-4" />;
}
