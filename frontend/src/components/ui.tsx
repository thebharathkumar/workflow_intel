import type { ReactNode } from "react";

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`rounded-xl border border-slate-800 bg-slate-900/60 p-5 ${className}`}>
      {children}
    </div>
  );
}

export function Section({
  title,
  subtitle,
  action,
  children,
}: {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="mb-8">
      <div className="mb-3 flex items-end justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-100">{title}</h2>
          {subtitle && <p className="text-sm text-slate-400">{subtitle}</p>}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

export function Stat({ label, value, hint }: { label: string; value: ReactNode; hint?: string }) {
  return (
    <Card className="text-center">
      <div className="text-2xl font-bold text-white">{value}</div>
      <div className="mt-1 text-xs uppercase tracking-wide text-slate-400">{label}</div>
      {hint && <div className="mt-1 text-[11px] text-slate-500">{hint}</div>}
    </Card>
  );
}

const TONE: Record<string, string> = {
  human: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  system: "bg-sky-500/15 text-sky-300 border-sky-500/30",
  ai_candidate: "bg-violet-500/15 text-violet-300 border-violet-500/30",
  low: "bg-slate-500/15 text-slate-300 border-slate-500/30",
  medium: "bg-yellow-500/15 text-yellow-300 border-yellow-500/30",
  high: "bg-orange-500/15 text-orange-300 border-orange-500/30",
  critical: "bg-rose-500/15 text-rose-300 border-rose-500/30",
  safe_for_full_automation: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  human_review_recommended: "bg-sky-500/15 text-sky-300 border-sky-500/30",
  human_approval_required: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  prohibited_automation: "bg-rose-500/15 text-rose-300 border-rose-500/30",
  neutral: "bg-slate-700/40 text-slate-300 border-slate-600/40",
};

export function Badge({ tone = "neutral", children }: { tone?: string; children: ReactNode }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-medium ${
        TONE[tone] ?? TONE.neutral
      }`}
    >
      {children}
    </span>
  );
}

export function ScoreBar({ label, value }: { label: string; value: number }) {
  const color = value >= 70 ? "bg-emerald-500" : value >= 45 ? "bg-yellow-500" : "bg-slate-500";
  return (
    <div>
      <div className="flex justify-between text-[11px] text-slate-400">
        <span>{label}</span>
        <span>{value}</span>
      </div>
      <div className="mt-1 h-1.5 w-full rounded-full bg-slate-800">
        <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

export function Spinner({ label = "Working…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-slate-400">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-slate-600 border-t-brand-500" />
      {label}
    </div>
  );
}

export function Pills({ items }: { items: string[] }) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((i) => (
        <span key={i} className="rounded-md bg-slate-800 px-2 py-0.5 text-xs text-slate-300">
          {i}
        </span>
      ))}
    </div>
  );
}

export function List({ items }: { items: string[] }) {
  return (
    <ul className="ml-4 list-disc space-y-1 text-sm text-slate-300">
      {items.map((i, idx) => (
        <li key={idx}>{i}</li>
      ))}
    </ul>
  );
}
