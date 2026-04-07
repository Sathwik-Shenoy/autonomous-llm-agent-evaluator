from fastapi import APIRouter, Depends

from app.api.deps import get_evaluation_service
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/environments", tags=["environments"])


@router.get("")
async def list_environments(service: EvaluationService = Depends(get_evaluation_service)) -> dict[str, list[str]]:
    return {"environments": service.environments.list()}
