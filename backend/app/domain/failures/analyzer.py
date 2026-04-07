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

    def replay_candidates(self, runs: list[AgentRunResult], threshold: float = 0.55) -> list[dict[str, object]]:
        candidates: list[dict[str, object]] = []
        for run in runs:
            if run.score.weighted_total > threshold:
                continue

            turn_failures = []
            for failure in run.failures:
                turn = run.turns[failure.turn_index] if 0 <= failure.turn_index < len(run.turns) else None
                turn_failures.append(
                    {
                        "category": failure.category,
                        "reason": failure.reason,
                        "turn_index": failure.turn_index,
                        "adversarial_tags": turn.adversarial_tags if turn else [],
                        "user_input": turn.user_input if turn else "",
                        "agent_output": turn.agent_output if turn else "",
                    }
                )

            candidates.append(
                {
                    "scenario_id": run.scenario_id,
                    "agent": run.agent.name,
                    "score": run.score.weighted_total,
                    "difficulty": run.difficulty,
                    "failures": turn_failures,
                }
            )
        return candidates
