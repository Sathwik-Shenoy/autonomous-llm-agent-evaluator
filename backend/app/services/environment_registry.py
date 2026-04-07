from __future__ import annotations

from app.domain.environments.base import BaseEnvironment
from app.domain.environments.code_review_env import CodeReviewEnvironment
from app.domain.environments.financial_env import FinancialDecisionEnvironment
from app.domain.environments.support_env import CustomerSupportEnvironment
from app.services.plugin_loader import load_environment_plugins


class EnvironmentRegistry:
    def __init__(self) -> None:
        self._environments: dict[str, BaseEnvironment] = {}
        self.register(CodeReviewEnvironment())
        self.register(FinancialDecisionEnvironment())
        self.register(CustomerSupportEnvironment())
        for plugin_env in load_environment_plugins():
            self.register(plugin_env)

    def register(self, env: BaseEnvironment) -> None:
        self._environments[env.name] = env

    def get(self, name: str) -> BaseEnvironment:
        if name not in self._environments:
            raise KeyError(f"Environment '{name}' is not registered")
        return self._environments[name]

    def list(self) -> list[str]:
        return sorted(self._environments.keys())
