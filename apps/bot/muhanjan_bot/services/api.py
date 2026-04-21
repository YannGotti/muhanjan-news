from __future__ import annotations

import httpx

from muhanjan_bot.config import settings


class BotApiError(RuntimeError):
    pass


class BotApiClient:
    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def startup(self) -> None:
        if self._client is not None:
            return

        connect_timeout = getattr(settings, "http_connect_timeout", settings.http_timeout)

        timeout = httpx.Timeout(
            timeout=settings.http_timeout,
            connect=connect_timeout,
        )

        self._client = httpx.AsyncClient(
            base_url=settings.api_base_url,
            timeout=timeout,
            headers={"Accept": "application/json"},
            limits=httpx.Limits(max_connections=40, max_keepalive_connections=20),
        )

    async def shutdown(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            await self.startup()
        return self._client  # type: ignore[return-value]

    async def request(self, method: str, path: str, **kwargs) -> httpx.Response:
        client = await self._ensure_client()
        try:
            return await client.request(method, path, **kwargs)
        except httpx.HTTPError as exc:
            raise BotApiError("network_error") from exc

    async def get(self, path: str) -> httpx.Response:
        return await self.request("GET", path)

    async def post(self, path: str, json_data: dict) -> httpx.Response:
        return await self.request("POST", path, json=json_data)


api_client = BotApiClient()


def extract_error_detail(response: httpx.Response) -> str | None:
    try:
        data = response.json()
    except Exception:
        return None

    detail = data.get("detail")
    return str(detail).strip() if detail else None
