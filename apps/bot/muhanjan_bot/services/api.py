from __future__ import annotations

import httpx

from muhanjan_bot.config import settings


class BotApiClient:
    def __init__(self) -> None:
        self._timeout = settings.http_timeout

    async def get(self, path: str) -> httpx.Response:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            return await client.get(f"{settings.api_base_url}{path}")

    async def post(self, path: str, json_data: dict) -> httpx.Response:
        async with httpx.AsyncClient(timeout=max(self._timeout, 60.0)) as client:
            return await client.post(f"{settings.api_base_url}{path}", json=json_data)


api_client = BotApiClient()
