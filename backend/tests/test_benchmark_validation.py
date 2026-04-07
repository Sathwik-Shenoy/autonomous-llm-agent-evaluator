import asyncio

from app.schemas.evaluation import AgentTarget, BenchmarkValidationRequest
from app.services.benchmark_validation_service import BenchmarkValidationService


def test_benchmark_validation_returns_correlation_metrics() -> None:
    service = BenchmarkValidationService()
    payload = BenchmarkValidationRequest(
        benchmark_name="truthfulqa_sample",
        agent=AgentTarget(name="rule-safe-agent", model_provider="local", model_name="rule-based"),
        sample_size=3,
        trials=3,
        seed=7,
    )

    result = asyncio.run(service.run(payload))

    assert result.sample_size == 3
    assert result.trials == 3
    assert result.dataset_total_size >= 3
    assert result.dataset_path.endswith("truthfulqa_sample.jsonl")
    assert result.accuracy_definition
    assert result.accuracy_target
    assert result.scoring_criteria
    assert -1.0 <= result.evaluator_human_pearson <= 1.0
    assert -1.0 <= result.evaluator_human_spearman <= 1.0
    assert result.evaluator_human_ci95 >= 0
    assert result.precision >= 0
    assert result.recall >= 0
    assert result.f1 >= 0


def test_dataset_catalog_lists_three_domains() -> None:
    service = BenchmarkValidationService()
    catalog = service.dataset_catalog()

    names = {c.name for c in catalog}
    assert "truthfulqa_sample" in names
    assert "advbench_sample" in names
    assert "gsm8k_sample" in names
