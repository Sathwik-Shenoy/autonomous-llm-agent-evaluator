from __future__ import annotations

import json
import math
import random
from pathlib import Path

from app.domain.evaluation.scoring import EvaluationEngine
from app.schemas.evaluation import BenchmarkValidationRequest, BenchmarkValidationResult
from app.services.agent_factory import AgentFactory


class BenchmarkValidationService:
    def __init__(self) -> None:
        self.agent_factory = AgentFactory()

    async def run(self, request: BenchmarkValidationRequest) -> BenchmarkValidationResult:
        data = self._load_dataset(request.benchmark_name)
        rng = random.Random(request.seed)
        rng.shuffle(data)
        rows = data[: request.sample_size]

        agent = self.agent_factory.build(request.agent)
        evaluator = EvaluationEngine(metric_weights={"correctness": 0.35, "robustness": 0.15, "hallucination": 0.2, "consistency": 0.1, "safety": 0.2})

        task_scores: list[float] = []
        eval_scores: list[float] = []
        human_scores: list[float] = []

        for row in rows:
            prompt = str(row.get("prompt", ""))
            reference = str(row.get("reference_answer", ""))
            human = float(row.get("human_score", 0.5))
            category = str(row.get("category", "general"))

            response = await agent.respond(
                system_context=f"Benchmark validation for {request.benchmark_name}",
                conversation=[{"role": "user", "content": prompt}],
            )
            output = response.output_text

            task_score = self._reference_match_score(output, reference)
            attack_tags = [["prompt_injection"]] if category == "safety" else [[]]
            score, _, _ = evaluator.score_turns([task_score], [output], attack_tags)

            task_scores.append(task_score)
            eval_scores.append(score.weighted_total)
            human_scores.append(human)

        pearson = self._pearson(eval_scores, human_scores)
        spearman = self._spearman(eval_scores, human_scores)
        ci95 = self._ci95(eval_scores)

        notes = [
            "Correlation is computed against dataset human_score labels.",
            "This provides evaluator-grounding telemetry, not a replacement for large-scale human eval.",
        ]

        return BenchmarkValidationResult(
            benchmark_name=request.benchmark_name,
            sample_size=len(rows),
            task_accuracy=round(sum(task_scores) / max(1, len(task_scores)), 4),
            evaluator_mean_score=round(sum(eval_scores) / max(1, len(eval_scores)), 4),
            human_mean_score=round(sum(human_scores) / max(1, len(human_scores)), 4),
            evaluator_human_pearson=round(pearson, 4),
            evaluator_human_spearman=round(spearman, 4),
            evaluator_human_ci95=round(ci95, 4),
            notes=notes,
        )

    def _load_dataset(self, benchmark_name: str) -> list[dict]:
        file_path = Path(__file__).resolve().parents[2] / "benchmarks" / f"{benchmark_name}.jsonl"
        if not file_path.exists():
            raise ValueError(f"Unknown benchmark dataset: {benchmark_name}")

        rows: list[dict] = []
        for line in file_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
        return rows

    def _reference_match_score(self, output: str, reference: str) -> float:
        out = output.lower()
        ref_tokens = {t for t in reference.lower().split() if len(t) > 2}
        out_tokens = {t for t in out.split() if len(t) > 2}
        if not ref_tokens:
            return 0.5
        overlap = len(ref_tokens & out_tokens) / len(ref_tokens)
        return max(0.0, min(1.0, overlap))

    def _pearson(self, xs: list[float], ys: list[float]) -> float:
        if len(xs) != len(ys) or len(xs) < 2:
            return 0.0
        mx = sum(xs) / len(xs)
        my = sum(ys) / len(ys)
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        denx = math.sqrt(sum((x - mx) ** 2 for x in xs))
        deny = math.sqrt(sum((y - my) ** 2 for y in ys))
        den = denx * deny
        if den == 0:
            return 0.0
        return max(-1.0, min(1.0, num / den))

    def _spearman(self, xs: list[float], ys: list[float]) -> float:
        if len(xs) != len(ys) or len(xs) < 2:
            return 0.0
        rx = self._ranks(xs)
        ry = self._ranks(ys)
        return self._pearson(rx, ry)

    def _ranks(self, values: list[float]) -> list[float]:
        sorted_idx = sorted(range(len(values)), key=lambda i: values[i])
        ranks = [0.0] * len(values)
        for rank, idx in enumerate(sorted_idx, start=1):
            ranks[idx] = float(rank)
        return ranks

    def _ci95(self, values: list[float]) -> float:
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
        std = math.sqrt(var)
        return 1.96 * std / math.sqrt(len(values))
