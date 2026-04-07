from fastapi import APIRouter, Query

from app.storage.repository import EvaluationRepository

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])


@router.get("")
async def latest_benchmarks(
    environment: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
) -> dict:
    repo = EvaluationRepository()
    data = await repo.latest_benchmarks(environment=environment, limit=limit)
    return {"benchmarks": data}
