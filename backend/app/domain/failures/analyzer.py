from __future__ import annotations

from collections import Counter

from app.schemas.evaluation import AgentRunResult


class FailureAnalyzer:
    def summarize(self, runs: list[AgentRunResult]) -> dict[str, dict[str, int]]:
        by_agent: dict[str, dict[str, int]] = {}
        for run in runs:
            counter = Counter(f.category for f in run.failures)
            by_agent[run.agent.name] = dict(counter)
        return by_agent

    def replay_candidates(self, runs: list[AgentRunResult], threshold: float = 0.55) -> list[str]:
        return [r.scenario_id for r in runs if r.score.weighted_total <= threshold]
