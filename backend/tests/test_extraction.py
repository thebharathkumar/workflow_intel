from workflow_intel.analysis.heuristics import extract_workflow
from workflow_intel.domain.enums import StepType


def test_extracts_actors_and_systems(example_text):
    wf = extract_workflow(example_text)
    actors = set(wf.actors)
    assert {"Sales", "Legal", "Finance"} <= actors
    system_names = {s["name"] for s in wf.systems}
    assert {"Salesforce", "Slack", "SharePoint"} <= system_names


def test_extracts_steps_in_order(example_text):
    wf = extract_workflow(example_text)
    assert len(wf.steps) >= 4
    assert [s.order for s in wf.steps] == sorted(s.order for s in wf.steps)
    # Legal "reviews" → a review step.
    assert any(s.type == StepType.REVIEW for s in wf.steps)


def test_classifies_storage_and_notification(example_text):
    wf = extract_workflow(example_text)
    types = {s.type for s in wf.steps}
    assert StepType.STORAGE in types  # "stored in SharePoint"
    assert StepType.NOTIFICATION in types  # "Slack notification"


def test_manual_data_entry_flagged(example_text):
    wf = extract_workflow(example_text)
    # "Sales updates Salesforce" → manual data entry into a system.
    data_entry = [s for s in wf.steps if s.type == StepType.DATA_ENTRY]
    assert data_entry
    assert any(s.is_manual and s.systems for s in data_entry)


def test_handles_empty_and_garbage():
    assert extract_workflow("").steps == []
    wf = extract_workflow("...;;,,")
    assert wf.steps == []
