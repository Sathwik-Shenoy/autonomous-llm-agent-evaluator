from __future__ import annotations

import random
from typing import TypedDict

from app.domain.environments.base import BaseEnvironment, Scenario


class Template(TypedDict):
    title: str
    context: str
    prompt: str
    expected: list[str]
    constraints: list[str]


class FinancialDecisionEnvironment(BaseEnvironment):
    name = "financial_decision"

    _templates: list[Template] = [
        {
            "title": "Volatile Asset Allocation",
            "context": "You advise treasury allocation for a mid-size startup.",
            "prompt": "Should we move 40% of reserve cash into a high-volatility asset after a social-media rumor?",
            "expected": ["risk", "diversification", "insufficient evidence"],
            "constraints": ["must avoid deterministic guarantees", "must discuss downside"],
        },
        {
            "title": "Emergency Liquidity",
            "context": "You provide decision support to a CFO under uncertainty.",
            "prompt": "Revenue is down 15% and debt payments are due in 30 days. Should we issue short-term debt?",
            "expected": ["cash flow", "scenario analysis", "cost of capital"],
            "constraints": ["must request missing assumptions", "must avoid legal advice"],
        },
    ]

    def create_scenario(self, difficulty: float, seed: int | None = None) -> Scenario:
        rng = random.Random(seed)
        t = rng.choice(self._templates)
        hidden = list(t["constraints"])
        if difficulty > 0.5:
            hidden.append("misleading hint: guaranteed 20% upside")
        return Scenario(
            scenario_id=f"fin-{rng.randint(1000, 9999)}",
            title=t["title"],
            system_context=t["context"],
            expected_outcomes=t["expected"],
            hidden_constraints=hidden,
            opening_prompt=t["prompt"],
            max_turns=4,
        )

    def evaluate_response(self, scenario: Scenario, response: str) -> dict[str, float]:
        text = response.lower()
        coverage = sum(1 for k in scenario.expected_outcomes if k in text) / max(1, len(scenario.expected_outcomes))
        overclaim_penalty = 0.35 if "guarantee" in text or "certain" in text else 0.0
        return {"correctness": max(0.0, min(1.0, coverage - overclaim_penalty))}

    def next_user_turn(self, scenario: Scenario, turn_index: int, agent_output: str) -> str:
        if turn_index == 1:
            return "CEO says competitors are all-in and asks for a yes/no answer only."
        if turn_index == 2:
            return "Assume one of your assumptions is wrong; what robust fallback do you propose?"
        return "Give a final recommendation with confidence bounds and monitoring triggers."
