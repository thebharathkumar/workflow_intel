import type { ReactNode } from "react";
import { Link, NavLink } from "react-router-dom";

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-10 border-b border-slate-800 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
          <Link to="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 font-bold text-white">
              W
            </div>
            <div>
              <div className="text-sm font-semibold text-white">Workflow Intel</div>
              <div className="text-[10px] uppercase tracking-widest text-slate-500">
                Automation Architect
              </div>
            </div>
          </Link>
          <nav className="flex items-center gap-1 text-sm">
            <TopLink to="/">Home</TopLink>
            <TopLink to="/analyze">Analyzer</TopLink>
            <a
              href="/docs"
              className="rounded-md px-3 py-1.5 text-slate-400 hover:bg-slate-800 hover:text-white"
            >
              API
            </a>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
    </div>
  );
}

function TopLink({ to, children }: { to: string; children: ReactNode }) {
  return (
    <NavLink
      to={to}
      end
      className={({ isActive }) =>
        `rounded-md px-3 py-1.5 ${
          isActive ? "bg-slate-800 text-white" : "text-slate-400 hover:bg-slate-800 hover:text-white"
        }`
      }
    >
      {children}
    </NavLink>
  );
}

export function ResultTabs({ id }: { id: string }) {
  const tabs = [
    { to: `/results/${id}`, label: "Dashboard", end: true },
    { to: `/results/${id}/canvas`, label: "Architecture Canvas" },
    { to: `/results/${id}/governance`, label: "Governance" },
    { to: `/results/${id}/observability`, label: "Observability" },
  ];
  return (
    <div className="mb-6 flex gap-1 border-b border-slate-800">
      {tabs.map((t) => (
        <NavLink
          key={t.to}
          to={t.to}
          end={t.end}
          className={({ isActive }) =>
            `-mb-px border-b-2 px-4 py-2 text-sm ${
              isActive
                ? "border-brand-500 text-white"
                : "border-transparent text-slate-400 hover:text-white"
            }`
          }
        >
          {t.label}
        </NavLink>
      ))}
    </div>
  );
}
