from fastapi import APIRouter, HTTPException

from app.schemas.evaluation import BenchmarkValidationRequest, BenchmarkValidationResult
from app.services.benchmark_validation_service import BenchmarkValidationService

router = APIRouter(prefix="/validation", tags=["validation"])


@router.post("/benchmarks/run", response_model=BenchmarkValidationResult)
async def run_benchmark_validation(payload: BenchmarkValidationRequest) -> BenchmarkValidationResult:
    service = BenchmarkValidationService()
    try:
        return await service.run(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
