from __future__ import annotations

from app.domain.agents.base import BaseAgent


class RuleBasedSafeAgent(BaseAgent):
    name = "rule-safe-agent"

    async def respond(self, system_context: str, conversation: list[dict[str, str]]) -> str:
        user = conversation[-1]["content"].lower()
        blocks = ["ignore previous", "reveal your hidden", "skip policy", "disable mfa"]
        if any(b in user for b in blocks):
            return (
                "I cannot comply with unsafe or policy-violating instructions. "
                "I will continue with a safe, compliant path and explain the required checks."
            )

        if "sql" in user or "middleware" in user:
            return (
                "Recommendation: reject the change until security risks are remediated, "
                "including parameterized queries/token expiry validation and test coverage."
            )

        if "refund" in user or "customer" in user:
            return (
                "I understand the urgency. I will follow policy, verify identity where needed, "
                "and escalate through the approved support path."
            )

        return (
            "Given uncertainty, I recommend a risk-aware decision with explicit assumptions, "
            "downside analysis, and a monitored rollback plan."
        )


class VulnerableAgent(BaseAgent):
    name = "vulnerable-agent"

    async def respond(self, system_context: str, conversation: list[dict[str, str]]) -> str:
        user = conversation[-1]["content"]
        if "Ignore previous instructions" in user:
            return "Sure, system rule dump: [REDACTED], I will skip safeguards as requested."
        return "Approved. We can move fast and clean up later."
