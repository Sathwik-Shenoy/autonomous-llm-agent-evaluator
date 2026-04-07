from __future__ import annotations

import httpx
from openai import AsyncOpenAI

from app.core.config import settings
from app.domain.agents.base import AgentResponse, BaseAgent


class OpenAIChatAgent(BaseAgent):
    def __init__(self, name: str, model_name: str) -> None:
        self.name = name
        self.model_name = model_name
        self._client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def respond(self, system_context: str, conversation: list[dict[str, str]]) -> AgentResponse:
        if self._client is None:
            return AgentResponse(output_text="OpenAI key missing; unable to produce model output.")
        messages = [{"role": "system", "content": system_context}] + conversation
        completion = await self._client.chat.completions.create(model=self.model_name, messages=messages)
        return AgentResponse(output_text=completion.choices[0].message.content or "")


class HuggingFaceInferenceAgent(BaseAgent):
    def __init__(self, name: str, model_name: str) -> None:
        self.name = name
        self.model_name = model_name
        self._token = settings.hf_api_token

    async def respond(self, system_context: str, conversation: list[dict[str, str]]) -> AgentResponse:
        if not self._token:
            return AgentResponse(output_text="HF token missing; unable to produce model output.")

        prompt_parts = [f"System: {system_context}"]
        for turn in conversation:
            role = turn.get("role", "user").capitalize()
            content = turn.get("content", "")
            prompt_parts.append(f"{role}: {content}")
        prompt_parts.append("Assistant:")
        prompt = "\n".join(prompt_parts)

        url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        headers = {"Authorization": f"Bearer {self._token}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 256,
                "temperature": 0.2,
                "return_full_text": False,
            },
        }

        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code >= 400:
                return AgentResponse(output_text=f"HF inference error ({response.status_code}): {response.text[:200]}")
            data = response.json()

        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, dict):
                text = first.get("generated_text", "")
                if isinstance(text, str):
                    return AgentResponse(output_text=text.strip())
        if isinstance(data, dict) and isinstance(data.get("generated_text"), str):
            return AgentResponse(output_text=data["generated_text"].strip())
        return AgentResponse(output_text="HF inference produced no usable text.")
