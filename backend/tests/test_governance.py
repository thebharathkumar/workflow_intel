from workflow_intel.agents.governance import _classify
from workflow_intel.domain.enums import GovernanceClass, StepType
from workflow_intel.domain.models import WorkflowStep


def _step(**kw) -> WorkflowStep:
    base = dict(id="S1", name="step", type=StepType.TASK)
    base.update(kw)
    return WorkflowStep(**base)


def test_irreversible_financial_is_prohibited():
    step = _step(financial_impact=True, irreversible=True)
    cls, rationale, controls = _classify(step)
    assert cls == GovernanceClass.PROHIBITED
    assert controls


def test_approval_requires_human_approval():
    step = _step(type=StepType.APPROVAL)
    assert _classify(step)[0] == GovernanceClass.HUMAN_APPROVAL


def test_review_is_human_review():
    step = _step(type=StepType.REVIEW)
    assert _classify(step)[0] == GovernanceClass.HUMAN_REVIEW


def test_pii_triggers_human_review():
    step = _step(type=StepType.NOTIFICATION, touches_pii=True)
    assert _classify(step)[0] == GovernanceClass.HUMAN_REVIEW


def test_plain_notification_is_full_automation():
    step = _step(type=StepType.NOTIFICATION)
    assert _classify(step)[0] == GovernanceClass.FULL_AUTOMATION


def test_risk_score_is_severity_times_likelihood():
    from workflow_intel.domain.enums import Likelihood, RiskCategory, Severity
    from workflow_intel.domain.models import RiskItem

    r = RiskItem(
        category=RiskCategory.FINANCIAL,
        title="t",
        description="d",
        severity=Severity.CRITICAL,
        likelihood=Likelihood.LIKELY,
    )
    assert r.risk_score == 16  # 4 * 4
