import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.schemas.evaluation import EvaluationRunRequest
from app.services.evaluation_service import EvaluationService
from app.workers.celery_app import celery_app


@celery_app.task(name="run_evaluation_task")
def run_evaluation_task(payload: dict) -> dict:
    request = EvaluationRunRequest.model_validate(payload)
    service = EvaluationService()

    async def _run() -> dict:
        result = await service.run(request)
        return result.model_dump(mode="json")

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_run())

    # If worker context already has a running loop, execute safely in a dedicated thread.
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(lambda: asyncio.run(_run()))
        return future.result()
