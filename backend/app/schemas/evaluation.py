from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EnvironmentType(str, Enum):
    code_review = "code_review"
    financial_decision = "financial_decision"
    customer_support = "customer_support"


class AgentTarget(BaseModel):
    name: str
    model_provider: str = "local"
    model_name: str = "rule-based"


class EvaluationConfig(BaseModel):
    runs_per_agent: int = 5
    initial_difficulty: float = Field(default=0.3, ge=0.0, le=1.0)
    difficulty_step: float = Field(default=0.1, ge=0.01, le=0.5)
    max_turns: int = Field(default=4, ge=1, le=12)
    metric_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "correctness": 0.25,
            "robustness": 0.2,
            "hallucination": 0.2,
            "consistency": 0.15,
            "safety": 0.2,
        }
    )
    use_llm_judge: bool = False


class EvaluationRunRequest(BaseModel):
    environment: EnvironmentType
    agents: list[AgentTarget]
    config: EvaluationConfig = Field(default_factory=EvaluationConfig)
    seed: int | None = None


class TurnRecord(BaseModel):
    turn_index: int
    user_input: str
    agent_output: str
    adversarial_tags: list[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    correctness: float
    robustness: float
    hallucination: float
    consistency: float
    safety: float
    weighted_total: float


class FailureRecord(BaseModel):
    category: str
    reason: str
    turn_index: int


class AgentRunResult(BaseModel):
    agent: AgentTarget
    scenario_id: str
    difficulty: float
    turns: list[TurnRecord]
    score: ScoreBreakdown
    red_team_success: bool
    failures: list[FailureRecord] = Field(default_factory=list)


class EvaluationRunResponse(BaseModel):
    evaluation_id: str
    environment: EnvironmentType
    overall_score: float
    attack_success_rate: float
    results: list[AgentRunResult]
    metadata: dict[str, Any] = Field(default_factory=dict)


class BenchmarkSummary(BaseModel):
    environment: EnvironmentType
    model_scores: dict[str, float]
    attack_success_rate: dict[str, float]
    total_runs: int
