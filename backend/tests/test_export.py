import json

import yaml

from workflow_intel.agents.coordinator import Coordinator
from workflow_intel.config import Settings
from workflow_intel.domain.models import AnalysisResult
from workflow_intel.export import SPEC_VERSION, to_json, to_spec, to_yaml


async def _result(text):
    return await Coordinator(Settings(llm_enabled=False)).analyze(text)


async def test_spec_contains_all_sections(example_text):
    spec = to_spec(await _result(example_text))
    assert spec["workflow_intel_spec_version"] == SPEC_VERSION
    for key in (
        "process",
        "workflow",
        "bottlenecks",
        "automation",
        "agents",
        "systems",
        "integrations",
        "governance",
        "risks",
        "observability",
        "evaluation",
        "diagrams",
        "metrics",
    ):
        assert key in spec
    assert spec["metrics"]["total_steps"] >= 4


async def test_json_export_is_valid(example_text):
    payload = json.loads(to_json(await _result(example_text)))
    assert payload["metadata"]["engine"] == "deterministic"


async def test_yaml_export_is_valid(example_text):
    payload = yaml.safe_load(to_yaml(await _result(example_text)))
    assert payload["workflow"]["steps"]


async def test_result_round_trips_through_json(example_text):
    result = await _result(example_text)
    dumped = result.model_dump(mode="json")
    restored = AnalysisResult.model_validate(dumped)
    assert restored.id == result.id
    assert len(restored.workflow.steps) == len(result.workflow.steps)
