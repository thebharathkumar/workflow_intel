# Evaluation Framework

The Evaluation Agent (`agents/evaluation.py`) generates a measurable eval suite for the
recommended automation. Each eval names a target, a metric, a KPI target, a method, a dataset, and
a cadence — so quality is quantified, not asserted.

| Eval | Target | Metric | KPI |
| --- | --- | --- | --- |
| Workflow extraction accuracy | workflow | step/actor/system F1 vs. golden | F1 ≥ 0.90 |
| Agent decision accuracy | agent | accuracy / Cohen's κ vs. expert | acc ≥ 0.90, κ ≥ 0.8 |
| Routing accuracy | routing | top-1 routing accuracy | ≥ 0.92 |
| Tool selection correctness | tool_selection | tool-choice accuracy + arg validity | ≥ 0.95 valid calls |
| Human escalation decisions | escalation | escalation precision & recall | P ≥ 0.85, R ≥ 0.90 |
| Automation success rate | automation_success | straight-through-processing rate | ≥ 0.80 STP, < 2% rollback |
| Groundedness / faithfulness | agent | citation check + LLM-judge | ≥ 0.95 |

## How evals are run
- **Golden datasets** — labeled workflow descriptions and decision cases, versioned alongside the
  code, expanded from production disagreements.
- **Trajectory evals** — recorded tool-call sequences are replayed and scored for correct tool
  choice and valid arguments (schema validation).
- **LLM-as-judge** — a calibrated rubric scores faithfulness/groundedness; citation verification
  backs the judge so the score is grounded.
- **Threshold sweeps** — the escalation confidence cutoff is set by sweeping precision/recall on
  the should-escalate set.

## Operating model
- Evals gate releases (CI) and run nightly against the golden set.
- Production cohorts feed STP/rollback/reopen metrics back into the dashboards (`observability.md`).
- Regressions page the owning team; the eval scores stream to Arize/Phoenix for drift tracking.

The same KPIs appear on the Results dashboard so a stakeholder sees, per analysis, exactly how the
recommended agents would be measured before anything ships.
