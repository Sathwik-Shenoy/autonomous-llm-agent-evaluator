from __future__ import annotations

import orjson
import redis.asyncio as redis

from app.core.config import settings


class RedisCache:
    def __init__(self) -> None:
        self.client = redis.from_url(settings.redis_url, decode_responses=False)

    async def set_json(self, key: str, value: dict, ttl: int = 3600) -> None:
        await self.client.set(key, orjson.dumps(value), ex=ttl)

    async def get_json(self, key: str) -> dict | None:
        data = await self.client.get(key)
        if not data:
            return None
        return orjson.loads(data)
