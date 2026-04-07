from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_evaluation_service
from app.schemas.evaluation import EvaluationRunRequest, EvaluationRunResponse
from app.services.evaluation_service import EvaluationService
from app.storage.repository import EvaluationRepository
from app.workers.tasks import run_evaluation_task

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post("/run", response_model=EvaluationRunResponse)
async def run_evaluation(
    payload: EvaluationRunRequest,
    service: EvaluationService = Depends(get_evaluation_service),
) -> EvaluationRunResponse:
    return await service.run(payload)


@router.post("/run-async")
async def run_evaluation_async(payload: EvaluationRunRequest) -> dict[str, str]:
    job = run_evaluation_task.delay(payload.model_dump(mode="json"))
    return {"task_id": job.id}


@router.get("/{evaluation_id}", response_model=EvaluationRunResponse)
async def get_evaluation(evaluation_id: str) -> EvaluationRunResponse:
    repo = EvaluationRepository()
    record = await repo.get_evaluation(evaluation_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return record
