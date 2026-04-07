from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "agent_evaluator",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
