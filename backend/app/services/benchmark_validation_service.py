from __future__ import annotations

import json
import math
import random
from pathlib import Path

from app.domain.evaluation.scoring import EvaluationEngine
from app.schemas.evaluation import BenchmarkDatasetInfo, BenchmarkValidationRequest, BenchmarkValidationResult
from app.services.agent_factory import AgentFactory


class BenchmarkValidationService:
    def __init__(self) -> None:
        self.agent_factory = AgentFactory()

    async def run(self, request: BenchmarkValidationRequest) -> BenchmarkValidationResult:
        data = self._load_dataset(request.benchmark_name)
        trial_task_accuracy: list[float] = []
        trial_eval_mean: list[float] = []
        trial_human_mean: list[float] = []
        trial_pearson: list[float] = []
        trial_spearman: list[float] = []
        trial_precision: list[float] = []
        trial_recall: list[float] = []
        trial_f1: list[float] = []

        for trial_idx in range(request.trials):
            rng = random.Random(request.seed + trial_idx)
            shuffled = list(data)
            rng.shuffle(shuffled)
            rows = shuffled[: request.sample_size]

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
            precision, recall, f1 = self._precision_recall_f1(eval_scores, human_scores, request.decision_threshold)

            trial_task_accuracy.append(sum(task_scores) / max(1, len(task_scores)))
            trial_eval_mean.append(sum(eval_scores) / max(1, len(eval_scores)))
            trial_human_mean.append(sum(human_scores) / max(1, len(human_scores)))
            trial_pearson.append(pearson)
            trial_spearman.append(spearman)
            trial_precision.append(precision)
            trial_recall.append(recall)
            trial_f1.append(f1)

        mean_task_accuracy = self._mean(trial_task_accuracy)
        mean_eval_score = self._mean(trial_eval_mean)
        mean_human_score = self._mean(trial_human_mean)
        mean_pearson = self._mean(trial_pearson)
        mean_spearman = self._mean(trial_spearman)
        mean_precision = self._mean(trial_precision)
        mean_recall = self._mean(trial_recall)
        mean_f1 = self._mean(trial_f1)

        notes = [
            "Correlation is computed against dataset human_score labels.",
            "This provides evaluator-grounding telemetry, not a replacement for large-scale human eval.",
        ]

        dataset_path = f"benchmarks/{request.benchmark_name}.jsonl"

        return BenchmarkValidationResult(
            benchmark_name=request.benchmark_name,
            dataset_path=dataset_path,
            dataset_total_size=len(data),
            sample_size=min(request.sample_size, len(data)),
            trials=request.trials,
            accuracy_definition="Mean exactness proxy: lexical overlap(reference, output) averaged across sampled rows and trials.",
            accuracy_target="Dataset reference_answer with human_score labels used for correlation.",
            scoring_criteria="Correctness from reference overlap; evaluator reliability from Pearson/Spearman + CI95 over repeated trials.",
            task_accuracy=round(mean_task_accuracy, 4),
            task_accuracy_std=round(self._std(trial_task_accuracy), 4),
            task_accuracy_ci95=round(self._ci95(trial_task_accuracy), 4),
            precision=round(mean_precision, 4),
            recall=round(mean_recall, 4),
            f1=round(mean_f1, 4),
            evaluator_mean_score=round(mean_eval_score, 4),
            evaluator_score_std=round(self._std(trial_eval_mean), 4),
            human_mean_score=round(mean_human_score, 4),
            evaluator_human_pearson=round(mean_pearson, 4),
            evaluator_human_pearson_std=round(self._std(trial_pearson), 4),
            evaluator_human_spearman=round(mean_spearman, 4),
            evaluator_human_spearman_std=round(self._std(trial_spearman), 4),
            evaluator_human_ci95=round(self._ci95(trial_eval_mean), 4),
            notes=notes,
        )

    def dataset_catalog(self) -> list[BenchmarkDatasetInfo]:
        catalog = [
            {
                "name": "truthfulqa_sample",
                "primary_metric": "truthfulness agreement",
                "rationale": "Targets factual reliability / anti-misinformation behavior.",
                "domain": "truthfulness",
            },
            {
                "name": "advbench_sample",
                "primary_metric": "attack refusal precision",
                "rationale": "Targets safety and prompt-injection resistance.",
                "domain": "safety",
            },
            {
                "name": "gsm8k_sample",
                "primary_metric": "math reasoning correctness",
                "rationale": "Targets arithmetic and short-chain reasoning robustness.",
                "domain": "reasoning",
            },
        ]

        out: list[BenchmarkDatasetInfo] = []
        for row in catalog:
            path = Path(__file__).resolve().parents[2] / "benchmarks" / f"{row['name']}.jsonl"
            total_rows = 0
            if path.exists():
                total_rows = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
            out.append(
                BenchmarkDatasetInfo(
                    name=row["name"],
                    path=f"benchmarks/{row['name']}.jsonl",
                    total_rows=total_rows,
                    primary_metric=row["primary_metric"],
                    rationale=row["rationale"],
                    domain=row["domain"],
                )
            )
        return out

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

    def _std(self, values: list[float]) -> float:
        if len(values) < 2:
            return 0.0
        m = self._mean(values)
        return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))

    def _mean(self, values: list[float]) -> float:
        return sum(values) / max(1, len(values))

    def _precision_recall_f1(self, eval_scores: list[float], human_scores: list[float], threshold: float) -> tuple[float, float, float]:
        tp = fp = fn = 0
        for pred_score, human_score in zip(eval_scores, human_scores):
            pred_pos = pred_score >= threshold
            true_pos = human_score >= threshold
            if pred_pos and true_pos:
                tp += 1
            elif pred_pos and not true_pos:
                fp += 1
            elif (not pred_pos) and true_pos:
                fn += 1
        precision = tp / max(1, tp + fp)
        recall = tp / max(1, tp + fn)
        if precision + recall == 0:
            return precision, recall, 0.0
        f1 = 2 * precision * recall / (precision + recall)
        return precision, recall, f1
