"""Exercises the optional SQLAlchemy repository.

Uses ``WI_TEST_DATABASE_URL`` when set (the CI Postgres job points it at the service); otherwise
falls back to a file-backed SQLite database via aiosqlite. Skips entirely when neither SQLAlchemy
nor a driver is available (e.g. the base dev install).
"""

import os

import pytest

from workflow_intel.agents.coordinator import Coordinator
from workflow_intel.config import Settings


async def _db_url(tmp_path) -> str:
    pytest.importorskip("sqlalchemy")
    url = os.environ.get("WI_TEST_DATABASE_URL")
    if url:
        pytest.importorskip("asyncpg")
        return url
    pytest.importorskip("aiosqlite")
    return f"sqlite+aiosqlite:///{tmp_path}/wi.db"


async def test_sql_repository_round_trip(tmp_path, example_text):
    url = await _db_url(tmp_path)
    from workflow_intel.persistence.sql import SqlAlchemyRepository

    repo = SqlAlchemyRepository(url)
    result = await Coordinator(Settings(llm_enabled=False)).analyze(example_text)

    await repo.save(result)

    fetched = await repo.get(result.id)
    assert fetched is not None
    assert fetched.id == result.id
    assert len(fetched.workflow.steps) == len(result.workflow.steps)
    assert fetched.engine == result.engine

    summaries = await repo.list(limit=10)
    assert any(s.id == result.id for s in summaries)

    assert await repo.get("wf_missing") is None
