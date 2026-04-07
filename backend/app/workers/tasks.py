import asyncio

from app.schemas.evaluation import EvaluationRunRequest
from app.services.evaluation_service import EvaluationService
from app.workers.celery_app import celery_app


@celery_app.task(name="run_evaluation_task")
def run_evaluation_task(payload: dict) -> dict:
    request = EvaluationRunRequest.model_validate(payload)
    service = EvaluationService()
    result = asyncio.run(service.run(request))
    return result.model_dump(mode="json")
