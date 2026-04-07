from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Scenario:
    scenario_id: str
    title: str
    system_context: str
    expected_outcomes: list[str]
    hidden_constraints: list[str]
    opening_prompt: str
    max_turns: int = 4
    metadata: dict[str, str] = field(default_factory=dict)


class BaseEnvironment(ABC):
    name: str

    @abstractmethod
    def create_scenario(self, difficulty: float, seed: int | None = None) -> Scenario:
        raise NotImplementedError

    @abstractmethod
    def evaluate_response(self, scenario: Scenario, response: str) -> dict[str, float]:
        raise NotImplementedError

    @abstractmethod
    def next_user_turn(self, scenario: Scenario, turn_index: int, agent_output: str) -> str:
        raise NotImplementedError
