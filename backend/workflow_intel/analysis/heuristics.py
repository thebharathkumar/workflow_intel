"""Rule-based extraction of structured workflow features from free text.

This is intentionally explainable: lexicons + ordered verb rules turn a prose description into
typed steps, actors, systems, and handoffs, with feature flags (manual, PII, financial,
irreversible, external) that downstream agents use for scoring, governance, and risk. The LLM
provider can replace this stage, but the system must be fully functional without it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from workflow_intel.domain.enums import ActorType, HandoffMechanism, StepType
from workflow_intel.knowledge.systems import match_systems

# --------------------------------------------------------------------------- #
# Lexicons
# --------------------------------------------------------------------------- #
TEAM_ACTORS = {
    "sales",
    "legal",
    "finance",
    "marketing",
    "hr",
    "human resources",
    "engineering",
    "procurement",
    "support",
    "operations",
    "ops",
    "it",
    "information technology",
    "compliance",
    "security",
    "accounting",
    "customer support",
    "customer success",
    "account management",
    "underwriting",
    "claims",
    "billing",
}
HUMAN_ACTORS = {
    "manager",
    "analyst",
    "employee",
    "approver",
    "reviewer",
    "accountant",
    "recruiter",
    "administrator",
    "admin",
    "executive",
    "account executive",
    "representative",
    "rep",
    "lead",
    "director",
    "team lead",
    "specialist",
    "officer",
    "agent",
}
EXTERNAL_ACTORS = {
    "customer",
    "client",
    "vendor",
    "supplier",
    "partner",
    "prospect",
    "applicant",
    "candidate",
}
ALL_ACTORS = TEAM_ACTORS | HUMAN_ACTORS | EXTERNAL_ACTORS

# Ordered: first match wins, so more specific types precede TASK.
VERB_RULES: list[tuple[StepType, tuple[str, ...]]] = [
    (
        StepType.APPROVAL,
        ("approve", "approval", "sign off", "sign-off", "authorize", "authorise", "sign the", "countersign"),
    ),
    (StepType.REVIEW, ("review", "verify", "validate", "vet", "assess", "evaluate", "examine", "audit", "inspect")),
    (
        StepType.DECISION,
        (
            "decide",
            "decision",
            "determine",
            "choose",
            "whether",
            "if approved",
            "triage",
            "route",
            "classify",
            "prioriti",
        ),
    ),
    (StepType.NOTIFICATION, ("notify", "notification", "alert", "inform", "ping", "remind", "escalate")),
    (StepType.STORAGE, ("store", "save", "archive", "upload", "file ", "attach", "deposit", "record in", "log in")),
    (
        StepType.DATA_ENTRY,
        (
            "update",
            "enter",
            "input",
            "re-enter",
            "reenter",
            "key in",
            "copy",
            "paste",
            "fill",
            "populate",
            "log the",
            "record the",
        ),
    ),
    (
        StepType.INTEGRATION,
        (
            "sync",
            "synchronise",
            "synchronize",
            "integrate",
            "push to",
            "pull from",
            "import",
            "export",
            "post to",
            "via api",
        ),
    ),
]

MECHANISM_RULES: list[tuple[HandoffMechanism, tuple[str, ...]]] = [
    (HandoffMechanism.EMAIL, ("email", "emails", "e-mail", "mails", "mail to", "forward")),
    (HandoffMechanism.CHAT, ("slack", "teams", "chat", "dm ", "direct message")),
    (HandoffMechanism.NOTIFICATION, ("notification", "notify", "alert", "ping", "remind")),
    (HandoffMechanism.TICKET, ("ticket", "jira", "servicenow", "service now", "zendesk", "case", "incident")),
    (
        HandoffMechanism.FILE_UPLOAD,
        ("upload", "sharepoint", "drive", "attach", "store in", "save to", "saved to", "stored in"),
    ),
    (HandoffMechanism.API, ("api", "webhook", "sync", "integrate", "push", "pull")),
    (HandoffMechanism.MEETING, ("meeting", "call", "standup", "stand-up", "sync up")),
]

PII_WORDS = (
    "ssn",
    "social security",
    "date of birth",
    "dob",
    "passport",
    "personal data",
    "personal information",
    "pii",
    "salary",
    "compensation",
    "health",
    "medical",
    "patient",
    "customer data",
    "employee data",
    "home address",
    "phone number",
    "credit card",
    "bank account",
)
FINANCIAL_WORDS = (
    "invoice",
    "payment",
    "payout",
    "refund",
    "wire",
    "pricing",
    "discount",
    "budget",
    "billing",
    "revenue",
    "purchase order",
    "po ",
    "expense",
    "reimburse",
    "salary",
    "payroll",
    "quote",
    "deal value",
    "contract value",
)
IRREVERSIBLE_WORDS = (
    "send",
    "sign",
    "submit",
    "pay",
    "delete",
    "purge",
    "post",
    "publish",
    "execute",
    "wire",
    "issue",
    "transfer",
    "deploy",
    "release",
    "finalize",
    "finalise",
    "dispatch",
)
MANUAL_WORDS = (
    "manual",
    "manually",
    "copy",
    "paste",
    "re-enter",
    "reenter",
    "by hand",
    "key in",
    "rekey",
    "re-key",
    "spreadsheet",
    "copy-paste",
)
REPETITIVE_WORDS = (
    "every",
    "each",
    "daily",
    "weekly",
    "monthly",
    "recurring",
    "routine",
    "repeat",
    "always",
    "whenever",
    "for each",
)
EXTERNAL_WORDS = EXTERNAL_ACTORS | {"external", "third party", "third-party", "outside"}

OBJECT_KEYWORDS = (
    "contract",
    "invoice",
    "comments",
    "comment",
    "notification",
    "record",
    "report",
    "ticket",
    "document",
    "payment",
    "purchase order",
    "order",
    "lead",
    "opportunity",
    "case",
    "file",
    "approval",
    "quote",
    "proposal",
    "agreement",
    "request",
    "ticket",
)


# --------------------------------------------------------------------------- #
# Result containers
# --------------------------------------------------------------------------- #
@dataclass
class ExtractedStep:
    id: str
    name: str
    description: str
    type: StepType
    actor: str | None
    actor_type: ActorType | None
    systems: list[str]
    order: int
    mechanism: HandoffMechanism | None
    target_actor: str | None
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    is_manual: bool = False
    is_external_comm: bool = False
    is_repetitive: bool = False
    touches_pii: bool = False
    financial_impact: bool = False
    irreversible: bool = False


@dataclass
class ExtractedWorkflow:
    steps: list[ExtractedStep]
    actors: dict[str, ActorType]
    systems: list[dict[str, Any]]


# --------------------------------------------------------------------------- #
# Extraction
# --------------------------------------------------------------------------- #
def _split_clauses(text: str) -> list[str]:
    raw = re.split(r"[.;\n]+", text)
    clauses: list[str] = []
    for sentence in raw:
        for part in re.split(r"\bthen\b", sentence, flags=re.IGNORECASE):
            part = part.strip(" ,")
            if part:
                clauses.append(part)
    return clauses


def _find_actors(clause: str) -> list[tuple[int, str, ActorType]]:
    lowered = clause.lower()
    hits: list[tuple[int, str, ActorType]] = []
    for actor in sorted(ALL_ACTORS, key=len, reverse=True):
        for m in re.finditer(rf"\b{re.escape(actor)}\b", lowered):
            atype = (
                ActorType.TEAM
                if actor in TEAM_ACTORS
                else ActorType.EXTERNAL
                if actor in EXTERNAL_ACTORS
                else ActorType.HUMAN
            )
            hits.append((m.start(), actor.title(), atype))
    hits.sort(key=lambda h: h[0])
    # de-dupe overlapping matches (e.g. "hr" inside "human resources")
    deduped: list[tuple[int, str, ActorType]] = []
    seen_spans: list[int] = []
    for pos, name, atype in hits:
        if pos not in seen_spans:
            deduped.append((pos, name, atype))
            seen_spans.append(pos)
    return deduped


def _classify_type(clause: str) -> StepType:
    lowered = clause.lower()
    for step_type, keywords in VERB_RULES:
        if any(k in lowered for k in keywords):
            return step_type
    if any(k in lowered for k in ("send", "email", "share", "deliver", "submit")):
        return StepType.TASK
    return StepType.TASK


def _detect_mechanism(clause: str) -> HandoffMechanism | None:
    lowered = clause.lower()
    for mechanism, keywords in MECHANISM_RULES:
        if any(k in lowered for k in keywords):
            return mechanism
    return None


def _detect_objects(clause: str) -> list[str]:
    lowered = clause.lower()
    found: list[str] = []
    for obj in OBJECT_KEYWORDS:
        if obj in lowered and obj.rstrip() not in [f.lower() for f in found]:
            found.append(obj.strip().title())
    return found[:3]


def _has(words: tuple[str, ...] | set[str], clause: str) -> bool:
    lowered = clause.lower()
    return any(w in lowered for w in words)


def compute_step_flags(text: str, step_type: StepType, actor_type: ActorType | None) -> dict[str, bool]:
    """Derive feature flags for a step from its text — shared by both extraction paths."""
    return {
        "is_manual": _has(MANUAL_WORDS, text)
        or (step_type == StepType.DATA_ENTRY and actor_type in (ActorType.HUMAN, ActorType.TEAM)),
        "is_external_comm": _has(EXTERNAL_WORDS, text) or actor_type == ActorType.EXTERNAL,
        "is_repetitive": _has(REPETITIVE_WORDS, text) or step_type in (StepType.DATA_ENTRY, StepType.NOTIFICATION),
        "touches_pii": _has(PII_WORDS, text),
        "financial_impact": _has(FINANCIAL_WORDS, text),
        "irreversible": _has(IRREVERSIBLE_WORDS, text)
        and (_has(EXTERNAL_WORDS, text) or _has(FINANCIAL_WORDS, text) or "contract" in text.lower()),
    }


def _clean_name(clause: str) -> str:
    name = re.sub(r"\s+", " ", clause).strip(" ,")
    name = re.sub(r"^(and|the|a|an)\s+", "", name, flags=re.IGNORECASE)
    if name:
        name = name[0].upper() + name[1:]
    return name[:140]


def extract_workflow(text: str) -> ExtractedWorkflow:
    """Parse ``text`` into a structured, feature-flagged workflow."""
    clauses = _split_clauses(text)
    systems = match_systems(text)
    actors: dict[str, ActorType] = {}
    steps: list[ExtractedStep] = []

    previous_actor: str | None = None
    previous_outputs: list[str] = []
    order = 0

    for clause in clauses:
        actor_hits = _find_actors(clause)
        step_systems = [s["name"] for s in match_systems(clause)]
        objects = _detect_objects(clause)

        # Skip fragments that carry no signal at all.
        if not actor_hits and not step_systems and not objects and len(clause.split()) < 3:
            continue

        subject = actor_hits[0] if actor_hits else None
        actor_name = subject[1] if subject else previous_actor
        actor_type = subject[2] if subject else None
        if actor_name and actor_type:
            actors[actor_name] = actor_type
        previous_actor = actor_name or previous_actor

        # Target actor = a distinct actor mentioned after the subject.
        target_actor = None
        for _pos, name, _ in actor_hits[1:]:
            if name != actor_name:
                target_actor = name
                break

        step_type = _classify_type(clause)
        mechanism = _detect_mechanism(clause)

        order += 1
        flags = compute_step_flags(clause, step_type, actor_type)
        step = ExtractedStep(
            id=f"S{order}",
            name=_clean_name(clause),
            description=clause.strip(),
            type=step_type,
            actor=actor_name,
            actor_type=actor_type,
            systems=step_systems,
            order=order,
            mechanism=mechanism,
            target_actor=target_actor,
            inputs=list(previous_outputs),
            outputs=objects or ([previous_outputs[0]] if previous_outputs else []),
            **flags,
        )
        steps.append(step)
        previous_outputs = step.outputs or previous_outputs

    return ExtractedWorkflow(steps=steps, actors=actors, systems=systems)
