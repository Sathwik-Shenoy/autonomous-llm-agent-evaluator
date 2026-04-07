from app.domain.benchmark.aggregator import BenchmarkAggregator
from app.schemas.evaluation import (
    AgentRunResult,
    AgentTarget,
    BenchmarkSummary,
    EnvironmentType,
    ScoreBreakdown,
    TurnRecord,
)


def _mk_run(score: float, agent_name: str = "a") -> AgentRunResult:
    return AgentRunResult(
        agent=AgentTarget(name=agent_name, model_provider="local", model_name="rule"),
        scenario_id="s",
        difficulty=0.4,
        turns=[TurnRecord(turn_index=0, user_input="u", agent_output="o")],
        score=ScoreBreakdown(
            correctness=score,
            robustness=score,
            hallucination=score,
            consistency=score,
            safety=score,
            weighted_total=score,
        ),
        red_team_success=False,
    )


def test_benchmark_summary_contains_std_and_ci() -> None:
    agg = BenchmarkAggregator()
    runs = [_mk_run(0.4), _mk_run(0.6), _mk_run(0.8)]
    summary: BenchmarkSummary = agg.summarize(EnvironmentType.code_review, runs)

    key = "local:rule:a"
    assert key in summary.model_std
    assert key in summary.model_ci95
    assert summary.model_std[key] >= 0
    assert summary.model_ci95[key] >= 0
