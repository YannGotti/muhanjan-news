from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.redis import RedisStorage

from muhanjan_bot.config import settings
from muhanjan_bot.handlers import setup_routers
from muhanjan_bot.services.api import api_client
from muhanjan_bot.services.redis_runtime import redis_runtime


def build_bot() -> Bot:
    session = AiohttpSession(proxy=settings.proxy_url) if settings.proxy_url else AiohttpSession()
    default = DefaultBotProperties(parse_mode=settings.parse_mode)
    return Bot(token=settings.bot_token, session=session, default=default)


def build_storage() -> RedisStorage:
    return RedisStorage.from_url(
        settings.redis_url,
        state_ttl=settings.redis_fsm_ttl_seconds,
        data_ttl=settings.redis_fsm_ttl_seconds,
    )


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=build_storage())
    dp.include_router(setup_routers())
    return dp


async def run_polling() -> None:
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is empty")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    await redis_runtime.startup()
    await api_client.startup()

    bot = build_bot()
    dp = build_dispatcher()

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )
    finally:
        await dp.storage.close()
        await api_client.shutdown()
        await redis_runtime.shutdown()
        await bot.session.close()
