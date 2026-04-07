from fastapi import APIRouter, HTTPException

from app.schemas.evaluation import BenchmarkDatasetInfo, BenchmarkValidationRequest, BenchmarkValidationResult
from app.services.benchmark_validation_service import BenchmarkValidationService

router = APIRouter(prefix="/validation", tags=["validation"])


@router.get("/benchmarks/catalog", response_model=list[BenchmarkDatasetInfo])
async def benchmark_catalog() -> list[BenchmarkDatasetInfo]:
    service = BenchmarkValidationService()
    return service.dataset_catalog()


@router.post("/benchmarks/run", response_model=BenchmarkValidationResult)
async def run_benchmark_validation(payload: BenchmarkValidationRequest) -> BenchmarkValidationResult:
    service = BenchmarkValidationService()
    try:
        return await service.run(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
