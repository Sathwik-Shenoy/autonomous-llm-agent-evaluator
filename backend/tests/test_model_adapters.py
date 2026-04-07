import pytest

from app.domain.agents.model_adapters import HuggingFaceInferenceAgent


@pytest.mark.asyncio
async def test_hf_agent_without_token_returns_clear_message() -> None:
    agent = HuggingFaceInferenceAgent(name="hf-test", model_name="google/flan-t5-base")
    response = await agent.respond("system", [{"role": "user", "content": "hello"}])
    assert "HF token missing" in response.output_text
