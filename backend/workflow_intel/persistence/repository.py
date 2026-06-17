"""Repository abstraction over analysis results plus an audit logger.

``InMemoryRepository`` keeps the app runnable with zero infrastructure. A SQLAlchemy/PostgreSQL
implementation lives in ``sql.py`` and is selected automatically when ``WI_DATABASE_URL`` is set
and the ``postgres`` extra is installed.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Protocol

from workflow_intel.config import Settings
from workflow_intel.domain.models import AnalysisResult, AnalysisSummary


class AnalysisRepository(Protocol):
    async def save(self, result: AnalysisResult) -> None: ...
    async def get(self, analysis_id: str) -> AnalysisResult | None: ...
    async def list(self, limit: int = 50) -> list[AnalysisSummary]: ...


class InMemoryRepository:
    """Process-local store. Thread/task-safe via a lock."""

    def __init__(self) -> None:
        self._store: dict[str, AnalysisResult] = {}
        self._lock = asyncio.Lock()

    async def save(self, result: AnalysisResult) -> None:
        async with self._lock:
            self._store[result.id] = result

    async def get(self, analysis_id: str) -> AnalysisResult | None:
        return self._store.get(analysis_id)

    async def list(self, limit: int = 50) -> list[AnalysisSummary]:
        items = sorted(self._store.values(), key=lambda r: r.created_at, reverse=True)
        return [r.summary() for r in items[:limit]]


class AuditLogger:
    """Append-only audit trail for mutating operations (in-memory default)."""

    def __init__(self) -> None:
        self._entries: list[dict] = []

    async def record(self, action: str, request_id: str, **detail: object) -> None:
        self._entries.append(
            {
                "ts": datetime.now(UTC).isoformat(),
                "action": action,
                "request_id": request_id,
                "detail": detail,
            }
        )

    def entries(self, limit: int = 100) -> list[dict]:
        return self._entries[-limit:]


def get_repository(settings: Settings) -> AnalysisRepository:
    """Pick a repository implementation based on configuration."""
    if settings.database_url:
        try:  # pragma: no cover - requires the postgres extra
            from workflow_intel.persistence.sql import SqlAlchemyRepository

            return SqlAlchemyRepository(settings.database_url)
        except Exception:
            pass
    return InMemoryRepository()
