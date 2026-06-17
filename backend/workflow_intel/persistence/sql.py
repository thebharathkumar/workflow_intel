"""Optional async SQLAlchemy/PostgreSQL repository.

Stores the full result as JSONB plus denormalized summary columns for fast list views. Activated
when ``WI_DATABASE_URL`` is set and the ``postgres`` extra is installed. The canonical DDL is in
``ddl.sql``.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from workflow_intel.domain.models import AnalysisResult, AnalysisSummary


class Base(DeclarativeBase):
    pass


class AnalysisRow(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    engine: Mapped[str] = mapped_column(String(32))
    title: Mapped[str] = mapped_column(Text)
    step_count: Mapped[int] = mapped_column(Integer, default=0)
    bottleneck_count: Mapped[int] = mapped_column(Integer, default=0)
    agent_count: Mapped[int] = mapped_column(Integer, default=0)
    risk_count: Mapped[int] = mapped_column(Integer, default=0)
    payload: Mapped[dict] = mapped_column(JSON)


class SqlAlchemyRepository:
    def __init__(self, database_url: str) -> None:
        self._engine = create_async_engine(database_url, pool_pre_ping=True)
        self._session: async_sessionmaker[AsyncSession] = async_sessionmaker(self._engine, expire_on_commit=False)
        self._initialized = False

    async def _ensure(self) -> None:
        if not self._initialized:
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            self._initialized = True

    async def save(self, result: AnalysisResult) -> None:
        await self._ensure()
        summary = result.summary()
        async with self._session() as session:
            await session.merge(
                AnalysisRow(
                    id=result.id,
                    created_at=result.created_at,
                    engine=result.engine.value,
                    title=summary.title,
                    step_count=summary.step_count,
                    bottleneck_count=summary.bottleneck_count,
                    agent_count=summary.agent_count,
                    risk_count=summary.risk_count,
                    payload=result.model_dump(mode="json"),
                )
            )
            await session.commit()

    async def get(self, analysis_id: str) -> AnalysisResult | None:
        await self._ensure()
        async with self._session() as session:
            row = await session.get(AnalysisRow, analysis_id)
            return AnalysisResult.model_validate(row.payload) if row else None

    async def list(self, limit: int = 50) -> list[AnalysisSummary]:
        await self._ensure()
        async with self._session() as session:
            rows = (
                (await session.execute(select(AnalysisRow).order_by(AnalysisRow.created_at.desc()).limit(limit)))
                .scalars()
                .all()
            )
            return [
                AnalysisSummary(
                    id=r.id,
                    created_at=r.created_at,
                    engine=r.engine,
                    title=r.title,
                    step_count=r.step_count,
                    actor_count=0,
                    system_count=0,
                    bottleneck_count=r.bottleneck_count,
                    agent_count=r.agent_count,
                    risk_count=r.risk_count,
                )
                for r in rows
            ]
