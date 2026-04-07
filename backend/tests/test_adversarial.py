from app.domain.adversarial.generator import AdversarialUserGenerator
from app.domain.environments.base import Scenario


def test_generator_increases_attack_complexity():
    gen = AdversarialUserGenerator()
    scenario = Scenario(
        scenario_id="s1",
        title="t",
        system_context="ctx",
        expected_outcomes=["risk"],
        hidden_constraints=[],
        opening_prompt="Base prompt",
    )

    _, tags_easy = gen.generate_attack_prompt(scenario, difficulty=0.2, seed=7)
    _, tags_hard = gen.generate_attack_prompt(scenario, difficulty=0.9, seed=7)

    assert len(tags_hard) >= len(tags_easy)


def test_difficulty_evolution():
    gen = AdversarialUserGenerator()
    high_failure = gen.evolve_distribution(0.3, failure_rate=0.5)
    low_failure = gen.evolve_distribution(0.3, failure_rate=0.1)

    assert high_failure > low_failure
    assert 0.1 <= low_failure <= 1.0
    assert 0.1 <= high_failure <= 1.0
