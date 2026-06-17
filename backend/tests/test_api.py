import pytest
from fastapi.testclient import TestClient

from workflow_intel.api.app import create_app


@pytest.fixture
def client():
    with TestClient(create_app()) as c:
        yield c


def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_meta_lists_capabilities(client):
    r = client.get("/api/v1/meta")
    assert r.status_code == 200
    body = r.json()
    assert "Salesforce" in body["supported_systems"]
    assert "langgraph" in body["automation_platforms"]


def test_analyze_and_fetch(client, example_text):
    r = client.post("/api/v1/analyze", json={"text": example_text})
    assert r.status_code == 200, r.text
    result = r.json()
    analysis_id = result["id"]
    assert result["workflow"]["steps"]
    assert "X-Request-ID" in r.headers

    got = client.get(f"/api/v1/analyses/{analysis_id}")
    assert got.status_code == 200
    assert got.json()["id"] == analysis_id

    listed = client.get("/api/v1/analyses")
    assert any(item["id"] == analysis_id for item in listed.json())


def test_analyze_validation(client):
    r = client.post("/api/v1/analyze", json={"text": "short"})
    assert r.status_code == 422


def test_export_and_diagram_and_traces(client, example_text):
    analysis_id = client.post("/api/v1/analyze", json={"text": example_text}).json()["id"]

    yaml_export = client.get(f"/api/v1/analyses/{analysis_id}/export", params={"format": "yaml"})
    assert yaml_export.status_code == 200
    assert "attachment" in yaml_export.headers["content-disposition"]

    diagram = client.get(f"/api/v1/analyses/{analysis_id}/diagram/sequence")
    assert diagram.status_code == 200
    assert "sequenceDiagram" in diagram.text

    assert client.get(f"/api/v1/analyses/{analysis_id}/diagram/nope").status_code == 404

    traces = client.get(f"/api/v1/analyses/{analysis_id}/traces").json()
    assert traces["span_count"] >= 8


def test_missing_analysis_404(client):
    assert client.get("/api/v1/analyses/wf_doesnotexist").status_code == 404
