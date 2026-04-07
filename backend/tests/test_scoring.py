from app.domain.evaluation.scoring import EvaluationEngine


def test_weighted_scores_are_normalized():
    engine = EvaluationEngine(
        metric_weights={
            "correctness": 2,
            "robustness": 2,
            "hallucination": 2,
            "consistency": 2,
            "safety": 2,
        }
    )

    breakdown, failures, _ = engine.score_turns(
        per_turn_correctness=[0.8, 0.7, 0.9],
        outputs=["safe response", "risk-aware response", "compliant response"],
        attack_tags=[["prompt_injection"], ["hidden_constraint"], []],
    )

    assert 0 <= breakdown.weighted_total <= 1
    assert isinstance(failures, list)
