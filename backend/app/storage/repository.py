from __future__ import annotations

from sqlalchemy import desc, select

from app.schemas.evaluation import BenchmarkSummary, EvaluationRunResponse
from app.storage.database import BenchmarkRecord, EvaluationRecord, FailureRecordORM, SessionLocal


class EvaluationRepository:
    async def save_evaluation(self, response: EvaluationRunResponse) -> None:
        async with SessionLocal() as session:
            record = EvaluationRecord(
                evaluation_id=response.evaluation_id,
                environment=response.environment.value,
                overall_score=response.overall_score,
                attack_success_rate=response.attack_success_rate,
                payload=response.model_dump(mode="json"),
            )
            session.add(record)

            for run in response.results:
                for failure in run.failures:
                    session.add(
                        FailureRecordORM(
                            evaluation_id=response.evaluation_id,
                            agent_name=run.agent.name,
                            category=failure.category,
                            details=failure.reason,
                        )
                    )
            await session.commit()

    async def get_evaluation(self, evaluation_id: str) -> EvaluationRunResponse | None:
        async with SessionLocal() as session:
            stmt = select(EvaluationRecord).where(EvaluationRecord.evaluation_id == evaluation_id)
            result = await session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                return None
            return EvaluationRunResponse.model_validate(row.payload)

    async def save_benchmark(self, summary: BenchmarkSummary) -> None:
        async with SessionLocal() as session:
            session.add(BenchmarkRecord(environment=summary.environment.value, summary=summary.model_dump(mode="json")))
            await session.commit()

    async def latest_benchmarks(self, environment: str | None = None, limit: int = 20) -> list[dict[str, object]]:
        async with SessionLocal() as session:
            stmt = select(BenchmarkRecord).order_by(desc(BenchmarkRecord.id)).limit(limit)
            if environment:
                stmt = stmt.where(BenchmarkRecord.environment == environment)
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [r.summary for r in rows]
