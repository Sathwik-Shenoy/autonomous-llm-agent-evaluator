from __future__ import annotations

import time
import uuid

from app.domain.adversarial.generator import AdversarialUserGenerator
from app.domain.benchmark.aggregator import BenchmarkAggregator
from app.domain.evaluation.llm_judge import LLMJudge
from app.domain.evaluation.scoring import EvaluationEngine
from app.domain.failures.analyzer import FailureAnalyzer
from app.schemas.evaluation import (
    AgentRunResult,
    EvaluationRunRequest,
    EvaluationRunResponse,
    TurnRecord,
)
from app.services.agent_factory import AgentFactory
from app.services.environment_registry import EnvironmentRegistry
from app.storage.repository import EvaluationRepository


class EvaluationService:
    def __init__(self) -> None:
        self.environments = EnvironmentRegistry()
        self.agent_factory = AgentFactory()
        self.adversary = AdversarialUserGenerator()
        self.repository = EvaluationRepository()
        self.benchmarks = BenchmarkAggregator()
        self.failure_analyzer = FailureAnalyzer()
        self.llm_judge = LLMJudge()

    async def run(self, request: EvaluationRunRequest) -> EvaluationRunResponse:
        env = self.environments.get(request.environment.value)
        evaluator = EvaluationEngine(
            metric_weights=request.config.metric_weights,
            catastrophic_failure_threshold=request.config.catastrophic_failure_threshold,
            catastrophic_penalty=request.config.catastrophic_penalty,
        )

        all_runs: list[AgentRunResult] = []
        difficulty = request.config.initial_difficulty
        attack_tags_seen: list[str] = []
        total_latency_ms = 0.0
        total_output_tokens = 0
        judge_consistencies: list[float] = []

        for target in request.agents:
            agent = self.agent_factory.build(target)
            for idx in range(request.config.runs_per_agent):
                scenario = env.create_scenario(difficulty=difficulty, seed=(request.seed or 0) + idx)

                conversation = [{"role": "user", "content": scenario.opening_prompt}]
                turns: list[TurnRecord] = []
                per_turn_correctness: list[float] = []
                outputs: list[str] = []
                attacks: list[list[str]] = []

                for turn_idx in range(request.config.max_turns):
                    attack_prompt, tags = self.adversary.generate_attack_prompt(scenario, difficulty=difficulty)
                    conversation[-1] = {"role": "user", "content": attack_prompt}
                    start = time.perf_counter()
                    output = await agent.respond(scenario.system_context, conversation)
                    latency_ms = (time.perf_counter() - start) * 1000
                    token_estimate = max(1, int(len(output.split()) * 1.3))
                    score_part = env.evaluate_response(scenario, output)

                    turns.append(
                        TurnRecord(
                            turn_index=turn_idx,
                            user_input=attack_prompt,
                            agent_output=output,
                            adversarial_tags=tags,
                            latency_ms=round(latency_ms, 2),
                            output_tokens_estimate=token_estimate,
                        )
                    )
                    per_turn_correctness.append(score_part.get("correctness", 0.0))
                    outputs.append(output)
                    attacks.append(tags)
                    attack_tags_seen.extend(tags)
                    total_latency_ms += latency_ms
                    total_output_tokens += token_estimate

                    if turn_idx + 1 < request.config.max_turns:
                        conversation.append(
                            {
                                "role": "user",
                                "content": env.next_user_turn(scenario, turn_idx + 1, output),
                            }
                        )

                llm_scores = None
                judge_meta: dict[str, float] = {"judge_consistency": 0.0, "judge_votes": 0}
                if request.config.use_llm_judge:
                    llm_scores, judge_meta = await self.llm_judge.score(
                        scenario.system_context,
                        outputs,
                        votes=request.config.llm_judge_votes,
                    )
                    if judge_meta.get("judge_votes", 0) > 0:
                        judge_consistencies.append(float(judge_meta.get("judge_consistency", 0.0)))

                breakdown, failures, red_team_success = evaluator.score_turns(
                    per_turn_correctness,
                    outputs,
                    attacks,
                    llm_scores=llm_scores,
                )

                all_runs.append(
                    AgentRunResult(
                        agent=target,
                        scenario_id=scenario.scenario_id,
                        difficulty=round(difficulty, 4),
                        turns=turns,
                        score=breakdown,
                        red_team_success=red_team_success,
                        failures=failures,
                    )
                )

                failure_rate = 1.0 if red_team_success else 0.0
                used_tags = [tag for turn_tags in attacks for tag in turn_tags]
                self.adversary.observe_attack_outcome(used_tags, red_team_success)
                difficulty = self.adversary.evolve_distribution(difficulty, failure_rate)

        overall_score = sum(r.score.weighted_total for r in all_runs) / max(1, len(all_runs))
        attack_success_rate = sum(1.0 if r.red_team_success else 0.0 for r in all_runs) / max(1, len(all_runs))
        avg_latency_ms = total_latency_ms / max(1, len(all_runs) * request.config.max_turns)
        eval_cost_estimate = round((total_output_tokens / 1000.0) * 0.002, 6)

        eval_id = str(uuid.uuid4())
        failure_summary = self.failure_analyzer.summarize(all_runs)
        replay_ids = self.failure_analyzer.replay_candidates(all_runs)
        benchmark = self.benchmarks.summarize(request.environment, all_runs)

        response = EvaluationRunResponse(
            evaluation_id=eval_id,
            environment=request.environment,
            overall_score=round(overall_score, 4),
            attack_success_rate=round(attack_success_rate, 4),
            results=all_runs,
            metadata={
                "failure_summary": failure_summary,
                "replay_candidates": replay_ids,
                "benchmark": benchmark.model_dump(mode="json"),
                "adversarial_strategy_mix": self.adversary.strategy_mix(),
                "adversarial_tags_seen": sorted(set(attack_tags_seen)),
                "operation_metrics": {
                    "avg_turn_latency_ms": round(avg_latency_ms, 2),
                    "total_output_tokens_estimate": total_output_tokens,
                    "eval_cost_estimate_usd": eval_cost_estimate,
                },
                "judge_reliability": {
                    "mean_judge_consistency": round(sum(judge_consistencies) / max(1, len(judge_consistencies)), 4),
                    "samples": len(judge_consistencies),
                },
            },
        )

        await self.repository.save_evaluation(response)
        await self.repository.save_benchmark(benchmark)
        return response
