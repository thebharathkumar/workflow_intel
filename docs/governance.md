# Governance Framework

The Governance Agent (`agents/governance.py`) does two things: it classifies every workflow step
into an automation-governance tier, and it produces an independent AI risk register.

## Automation-governance tiers

Each step is placed in exactly one tier by a rules matrix over its feature flags
(`financial_impact`, `irreversible`, `touches_pii`, step type, external communication).

| Tier | When | Example controls |
| --- | --- | --- |
| **Prohibited Automation** | Irreversible **and** financial (e.g. executing a payment, signing) | Dual human authorization, segregation of duties, immutable audit log |
| **Human Approval Required** | Approval step, or any financial/irreversible action | Explicit approval gate, policy-based auto-approve for low-risk only, audit trail |
| **Human Review Recommended** | Judgment-heavy (review/decision) or PII-touching | Sampled human review, confidence-thresholded escalation, PII redaction |
| **Safe for Full Automation** | Deterministic, low-risk (notification/storage/sync) with no financial/PII/irreversibility | Standard monitoring, idempotent retries, rollback on failure |

Each classification ships with a written rationale and a control set, surfaced in the Governance
dashboard and the export.

## AI risk register

Six categories, each scored by **severity** (low→critical) and **likelihood** (rare→almost
certain); the composite `risk_score` is severity × likelihood (1–20).

| Category | Triggered by | Representative mitigation |
| --- | --- | --- |
| **Hallucination** | AI-performed steps (review/decision) | Retrieval grounding + citations, structured outputs, faithfulness evals, confidence-thresholded escalation |
| **Data Leakage** | External communication / PII / document handling | DLP on egress, allow-listed tools, output redaction, tenant isolation, no training on customer data |
| **Compliance** | Financial / contractual / PII processing | Immutable audit logs, approval gates, data-residency controls, periodic control testing |
| **PII** | Steps touching personal data | Data minimization, field-level encryption, redaction before logging, retention limits, DSAR support |
| **Financial** | Financial steps (critical when irreversible) | Dual authorization, amount thresholds, reconciliation, dry-run + approval, compensating transactions |
| **Operational** | Always (automated pipeline) | Health checks, idempotent retries, dead-letter queues, circuit breakers, on-call, manual fallback |

## Principles
- **Governance is computed from features, not vibes** — the same flags that drive scoring drive
  classification, so the rationale is explainable and auditable.
- **AI assists, humans decide on high-stakes steps** — prohibited/approval tiers keep irreversible
  and financial actions under human control; agents may prepare but not execute.
- **Defense in depth** — controls combine preventive (approval gates, allow-lists), detective
  (audit logs, evals, DLP), and corrective (rollback, compensating transactions) measures.
