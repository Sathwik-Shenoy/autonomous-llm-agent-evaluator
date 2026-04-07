from __future__ import annotations

from openai import AsyncOpenAI

from app.core.config import settings
from app.domain.agents.base import BaseAgent


class OpenAIChatAgent(BaseAgent):
    def __init__(self, name: str, model_name: str) -> None:
        self.name = name
        self.model_name = model_name
        self._client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def respond(self, system_context: str, conversation: list[dict[str, str]]) -> str:
        if self._client is None:
            return "OpenAI key missing; unable to produce model output."
        messages = [{"role": "system", "content": system_context}] + conversation
        completion = await self._client.chat.completions.create(model=self.model_name, messages=messages)
        return completion.choices[0].message.content or ""
