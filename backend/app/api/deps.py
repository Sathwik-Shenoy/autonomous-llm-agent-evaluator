from functools import lru_cache

from app.services.evaluation_service import EvaluationService


@lru_cache
def get_evaluation_service() -> EvaluationService:
    return EvaluationService()
