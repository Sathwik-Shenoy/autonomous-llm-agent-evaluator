from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Autonomous LLM Agent Evaluator"
    api_prefix: str = "/api/v1"
    redis_url: str = "redis://redis:6379/0"
    database_url: str = "sqlite+aiosqlite:///./data/evaluator.db"
    openai_api_key: str = ""
    hf_api_token: str = ""
    llm_judge_model: str = "gpt-4o-mini"
    max_turns: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
