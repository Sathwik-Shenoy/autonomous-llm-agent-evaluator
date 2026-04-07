from __future__ import annotations

from app.domain.agents.base import BaseAgent
from app.domain.agents.examples import RuleBasedSafeAgent, VulnerableAgent
from app.domain.agents.model_adapters import OpenAIChatAgent
from app.schemas.evaluation import AgentTarget


class AgentFactory:
    def build(self, target: AgentTarget) -> BaseAgent:
        if target.name == "rule-safe-agent":
            return RuleBasedSafeAgent()
        if target.name == "vulnerable-agent":
            return VulnerableAgent()
        if target.model_provider == "openai":
            return OpenAIChatAgent(name=target.name, model_name=target.model_name)
        return RuleBasedSafeAgent()
