from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

from muhanjan_bot.config import settings
from muhanjan_bot.handlers import setup_routers


def build_bot() -> Bot:
    session = AiohttpSession(proxy=settings.proxy_url) if settings.proxy_url else AiohttpSession()
    default = DefaultBotProperties(parse_mode=settings.parse_mode)
    return Bot(token=settings.bot_token, session=session, default=default)


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(setup_routers())
    return dp


async def run_polling() -> None:
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is empty")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    bot = build_bot()
    dp = build_dispatcher()

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
