"""Command-line entry point: ``python -m workflow_intel.cli analyze "..."``."""

from __future__ import annotations

import argparse
import asyncio
import sys

from workflow_intel.agents.coordinator import Coordinator
from workflow_intel.config import get_settings
from workflow_intel.domain.models import AnalysisResult
from workflow_intel.export import to_json, to_yaml


def _print_summary(result: AnalysisResult) -> None:
    r = result
    print("=" * 78)
    print(f"WORKFLOW INTEL  ·  engine={r.engine.value}  ·  model={r.model or 'n/a'}")
    print("=" * 78)
    print(f"\nSummary: {r.process_report.summary}")
    print(f"Objective: {r.process_report.business_objective}\n")
    print(f"Steps ({len(r.workflow.steps)}):")
    for s in r.workflow.steps:
        sys_str = f" [{', '.join(s.systems)}]" if s.systems else ""
        print(f"  {s.id}. {s.name}  ({s.type.value}; actor={s.actor or '-'}){sys_str}")

    print(f"\nTop bottlenecks ({len(r.bottlenecks)}):")
    for b in sorted(r.bottlenecks, key=lambda x: x.impact_score, reverse=True)[:6]:
        print(f"  [{b.type.value:>12}] {b.title}")
        print(
            f"               impact={b.impact_score} complexity={b.complexity_score} "
            f"confidence={b.confidence_score} ROI={b.estimated_roi}"
        )

    print(f"\nDesigned agents ({len(r.agents)}):")
    for a in r.agents:
        print(f"  - {a.name}: {a.purpose}")

    print(f"\nGovernance ({len(r.governance)} steps):")
    counts: dict[str, int] = {}
    for g in r.governance:
        counts[g.classification.value] = counts.get(g.classification.value, 0) + 1
    for k, v in counts.items():
        print(f"  {k}: {v}")

    print(f"\nRisks ({len(r.risks)}):")
    for risk in r.risks:
        print(f"  [{risk.severity.value:>8}/{risk.likelihood.value:<14}] {risk.category.value}: {risk.title}")

    total_hours = sum(b.annual_hours_saved for b in r.bottlenecks)
    print(f"\nEstimated annual hours saved: {total_hours:.0f}")
    print(
        f"Pipeline trace: {len(r.trace)} spans, "
        f"{sum(t.latency_ms for t in r.trace):.1f} ms, "
        f"${sum(t.cost_usd_estimate for t in r.trace):.4f}"
    )
    print("=" * 78)


async def _run(text: str, fmt: str) -> int:
    coordinator = Coordinator(get_settings())
    result = await coordinator.analyze(text)
    if fmt == "json":
        print(to_json(result))
    elif fmt == "yaml":
        print(to_yaml(result))
    else:
        _print_summary(result)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="workflow-intel", description="Analyze a business workflow.")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze", help="Analyze a workflow description")
    analyze.add_argument("text", help="The workflow description (quote it)")
    analyze.add_argument("--format", choices=["summary", "json", "yaml"], default="summary")
    args = parser.parse_args(argv)

    if args.command == "analyze":
        return asyncio.run(_run(args.text, args.format))
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
