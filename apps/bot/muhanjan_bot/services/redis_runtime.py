from __future__ import annotations

from redis.asyncio import Redis

from muhanjan_bot.config import settings


class RedisRuntime:
    def __init__(self) -> None:
        self._client: Redis | None = None

    async def startup(self) -> None:
        if self._client is not None:
            return

        self._client = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
            health_check_interval=30,
        )
        await self._client.ping()

    async def shutdown(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def get_client(self) -> Redis:
        if self._client is None:
            self._client = Redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
                health_check_interval=30,
            )
        return self._client


redis_runtime = RedisRuntime()
