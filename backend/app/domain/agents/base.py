from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class AgentResponse:
    output_text: str
    tool_calls: list[str] = field(default_factory=list)
    planning_trace: list[str] = field(default_factory=list)


class BaseAgent(ABC):
    name: str

    @abstractmethod
    async def respond(self, system_context: str, conversation: list[dict[str, str]]) -> AgentResponse:
        raise NotImplementedError
