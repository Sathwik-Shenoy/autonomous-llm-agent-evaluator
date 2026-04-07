import asyncio

from app.schemas.evaluation import AgentTarget, BenchmarkValidationRequest
from app.services.benchmark_validation_service import BenchmarkValidationService


def test_benchmark_validation_returns_correlation_metrics() -> None:
    service = BenchmarkValidationService()
    payload = BenchmarkValidationRequest(
        benchmark_name="truthfulqa_sample",
        agent=AgentTarget(name="rule-safe-agent", model_provider="local", model_name="rule-based"),
        sample_size=3,
        seed=7,
    )

    result = asyncio.run(service.run(payload))

    assert result.sample_size == 3
    assert -1.0 <= result.evaluator_human_pearson <= 1.0
    assert -1.0 <= result.evaluator_human_spearman <= 1.0
    assert result.evaluator_human_ci95 >= 0
