from __future__ import annotations

from aiogram.types import Message

from muhanjan_bot.services.api import api_client


async def ensure_remote_user(message: Message) -> dict:
    payload = {
        "telegram_id": message.from_user.id,
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name,
    }
    response = await api_client.post("/bot/users/upsert", payload)
    response.raise_for_status()
    return response.json()


async def fetch_user_state(telegram_id: int) -> dict:
    response = await api_client.get(f"/bot/users/{telegram_id}")
    response.raise_for_status()
    return response.json()


async def update_twitch_nickname(telegram_id: int, nickname: str) -> dict:
    response = await api_client.post(
        "/bot/users/twitch",
        {
            "telegram_id": telegram_id,
            "twitch_nickname": nickname,
        },
    )
    response.raise_for_status()
    return response.json()
