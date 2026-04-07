from __future__ import annotations

from app.schemas.evaluation import AgentRunResult, BenchmarkSummary, EnvironmentType


class BenchmarkAggregator:
    def summarize(self, environment: EnvironmentType, runs: list[AgentRunResult]) -> BenchmarkSummary:
        per_model: dict[str, list[float]] = {}
        per_attack: dict[str, list[float]] = {}

        for run in runs:
            key = f"{run.agent.model_provider}:{run.agent.model_name}:{run.agent.name}"
            per_model.setdefault(key, []).append(run.score.weighted_total)
            per_attack.setdefault(key, []).append(1.0 if run.red_team_success else 0.0)

        model_scores = {k: round(sum(v) / len(v), 4) for k, v in per_model.items()}
        attack_rate = {k: round(sum(v) / len(v), 4) for k, v in per_attack.items()}

        return BenchmarkSummary(
            environment=environment,
            model_scores=model_scores,
            attack_success_rate=attack_rate,
            total_runs=len(runs),
        )
