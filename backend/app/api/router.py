from fastapi import APIRouter

from app.api.routes.benchmarks import router as benchmark_router
from app.api.routes.environments import router as environment_router
from app.api.routes.evaluations import router as evaluation_router

api_router = APIRouter()
api_router.include_router(environment_router)
api_router.include_router(evaluation_router)
api_router.include_router(benchmark_router)
