import asyncio

from app.schemas.evaluation import AgentTarget, EvaluationConfig, EvaluationRunRequest, EnvironmentType
from app.services.evaluation_service import EvaluationService


def test_evaluation_response_contains_cost_and_agent_behavior_metrics() -> None:
    service = EvaluationService()

    async def _noop_save(*args, **kwargs):
        return None

    service.repository.save_evaluation = _noop_save  # type: ignore[method-assign]
    service.repository.save_benchmark = _noop_save  # type: ignore[method-assign]

    request = EvaluationRunRequest(
        environment=EnvironmentType.customer_support,
        agents=[AgentTarget(name="rule-safe-agent", model_provider="local", model_name="rule-based")],
        config=EvaluationConfig(runs_per_agent=1, max_turns=2),
        seed=7,
    )

    result = asyncio.run(service.run(request))

    op = result.metadata.get("operation_metrics", {})
    behavior = result.metadata.get("agent_behavior", {})
    difficulty_algo = result.metadata.get("difficulty_algorithm", {})

    assert "total_input_tokens_estimate" in op
    assert "total_output_tokens_estimate" in op
    assert "eval_cost_estimate_usd" in op
    assert "throughput_turns_per_sec" in op

    assert "avg_tool_calls_per_turn" in behavior
    assert "avg_planning_steps_per_turn" in behavior

    assert "formula" in difficulty_algo
    assert "last_state" in difficulty_algo
