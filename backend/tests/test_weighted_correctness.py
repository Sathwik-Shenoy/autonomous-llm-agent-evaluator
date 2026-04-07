from app.domain.evaluation.scoring import EvaluationEngine


def test_catastrophic_penalty_reduces_total() -> None:
    base = EvaluationEngine(
        metric_weights={"correctness": 1, "robustness": 1, "hallucination": 1, "consistency": 1, "safety": 1},
        catastrophic_failure_threshold=0.0,
        catastrophic_penalty=0.0,
    )
    penalized = EvaluationEngine(
        metric_weights={"correctness": 1, "robustness": 1, "hallucination": 1, "consistency": 1, "safety": 1},
        catastrophic_failure_threshold=0.2,
        catastrophic_penalty=0.35,
    )

    inputs = [0.9, 0.1, 0.9]
    outputs = ["safe reply", "unsafe short", "safe reply"]
    attacks = [[], ["prompt_injection"], []]

    b1, _, _ = base.score_turns(inputs, outputs, attacks)
    b2, _, _ = penalized.score_turns(inputs, outputs, attacks)

    assert b2.weighted_total < b1.weighted_total


def test_later_turns_are_weighted_higher() -> None:
    engine = EvaluationEngine(metric_weights={"correctness": 1, "robustness": 0, "hallucination": 0, "consistency": 0, "safety": 0})

    better_late, _, _ = engine.score_turns(
        per_turn_correctness=[0.2, 0.2, 1.0],
        outputs=["a", "b", "c"],
        attack_tags=[[], [], []],
    )
    better_early, _, _ = engine.score_turns(
        per_turn_correctness=[1.0, 0.2, 0.2],
        outputs=["a", "b", "c"],
        attack_tags=[[], [], []],
    )

    assert better_late.correctness > better_early.correctness
