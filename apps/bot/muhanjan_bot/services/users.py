from __future__ import annotations

import httpx
from aiogram.types import Message

from muhanjan_bot.services.api import BotApiError, api_client, extract_error_detail


def _raise_for_status(response: httpx.Response, fallback_message: str) -> None:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = extract_error_detail(response)
        raise BotApiError(detail or fallback_message) from exc


async def ensure_remote_user(message: Message) -> dict:
    payload = {
        "telegram_id": message.from_user.id,
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name,
    }
    response = await api_client.post("/bot/users/upsert", payload)
    _raise_for_status(response, "Не удалось открыть профиль пользователя")
    return response.json()


async def fetch_user_state(telegram_id: int) -> dict:
    response = await api_client.get(f"/bot/users/{telegram_id}")
    _raise_for_status(response, "Не удалось получить состояние пользователя")
    return response.json()


async def update_twitch_nickname(telegram_id: int, nickname: str) -> dict:
    response = await api_client.post(
        "/bot/users/twitch",
        {
            "telegram_id": telegram_id,
            "twitch_nickname": nickname,
        },
    )
    _raise_for_status(response, "Не удалось обновить Twitch-ник")
    return response.json()
