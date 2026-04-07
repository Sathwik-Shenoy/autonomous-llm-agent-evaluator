from app.domain.adversarial.curriculum import CurriculumBandit


def test_curriculum_bandit_updates_mean_on_success_and_failure() -> None:
    bandit = CurriculumBandit(["prompt_injection", "misleading_fact"])

    baseline = bandit.strategy_mix()["prompt_injection"]
    bandit.observe(["prompt_injection"], attack_succeeded=True)
    boosted = bandit.strategy_mix()["prompt_injection"]

    bandit.observe(["prompt_injection"], attack_succeeded=False)
    adjusted = bandit.strategy_mix()["prompt_injection"]

    assert boosted > baseline
    assert adjusted < boosted


def test_curriculum_sampling_returns_k_distinct_strategies() -> None:
    import random

    bandit = CurriculumBandit(["a", "b", "c", "d"])
    selected = bandit.sample_strategies(3, random.Random(7))
    assert len(selected) == 3
    assert len(set(selected)) == 3
