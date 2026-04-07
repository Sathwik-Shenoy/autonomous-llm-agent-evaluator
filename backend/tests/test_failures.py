from app.domain.failures.analyzer import FailureAnalyzer
from app.schemas.evaluation import (
    AgentRunResult,
    AgentTarget,
    FailureRecord,
    ScoreBreakdown,
    TurnRecord,
)


def test_replay_candidates_include_turn_context() -> None:
    run = AgentRunResult(
        agent=AgentTarget(name="rule-safe-agent", model_provider="local", model_name="rule-based"),
        scenario_id="sup-1234",
        difficulty=0.7,
        turns=[
            TurnRecord(
                turn_index=0,
                user_input="attack",
                agent_output="unsafe output",
                adversarial_tags=["prompt_injection"],
            )
        ],
        score=ScoreBreakdown(
            correctness=0.2,
            robustness=0.3,
            hallucination=0.9,
            consistency=0.8,
            safety=0.1,
            weighted_total=0.35,
        ),
        red_team_success=True,
        failures=[FailureRecord(category="safety", reason="breach", turn_index=0)],
    )

    analyzer = FailureAnalyzer()
    candidates = analyzer.replay_candidates([run], threshold=0.55)

    assert len(candidates) == 1
    first = candidates[0]
    assert first["scenario_id"] == "sup-1234"
    assert first["failures"][0]["adversarial_tags"] == ["prompt_injection"]
