from __future__ import annotations

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    name: str

    @abstractmethod
    async def respond(self, system_context: str, conversation: list[dict[str, str]]) -> str:
        raise NotImplementedError
