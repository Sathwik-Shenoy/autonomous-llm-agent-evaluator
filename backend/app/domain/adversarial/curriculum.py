from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass
class StrategyPosterior:
    alpha: float = 1.0
    beta: float = 1.0

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)


class CurriculumBandit:
    """Tracks adversarial strategy effectiveness and samples attacks via Thompson sampling."""

    def __init__(self, strategies: list[str]) -> None:
        self._strategies = strategies
        self._posteriors = {s: StrategyPosterior() for s in strategies}

    def sample_strategies(self, k: int, rng: random.Random) -> list[str]:
        scored = []
        for strategy, posterior in self._posteriors.items():
            sample = rng.betavariate(posterior.alpha, posterior.beta)
            scored.append((sample, strategy))
        scored.sort(reverse=True)
        return [s for _, s in scored[:k]]

    def observe(self, used_strategies: list[str], attack_succeeded: bool) -> None:
        for strategy in used_strategies:
            posterior = self._posteriors.get(strategy)
            if posterior is None:
                continue
            if attack_succeeded:
                posterior.alpha += 1
            else:
                posterior.beta += 1

    def pressure(self) -> float:
        means = [p.mean for p in self._posteriors.values()]
        return sum(means) / max(1, len(means))

    def strategy_mix(self) -> dict[str, float]:
        raw = {s: p.mean for s, p in self._posteriors.items()}
        total = sum(raw.values()) or 1.0
        return {s: round(v / total, 4) for s, v in raw.items()}

    def entropy(self) -> float:
        mix = self.strategy_mix()
        e = 0.0
        for p in mix.values():
            if p > 0:
                e -= p * math.log(p)
        max_entropy = math.log(max(2, len(mix)))
        return e / max_entropy
