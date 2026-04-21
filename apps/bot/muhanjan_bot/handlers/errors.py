from __future__ import annotations

import logging

from aiogram import Router
from aiogram.types import ErrorEvent

from muhanjan_bot import texts
from muhanjan_bot.keyboards.reply import main_menu_keyboard

router = Router(name="errors")
logger = logging.getLogger(__name__)


@router.errors()
async def error_handler(event: ErrorEvent):
    logger.exception("Unhandled bot error", exc_info=event.exception)

    update = event.update
    message = getattr(update, "message", None)
    error_text = getattr(
        texts,
        "GENERIC_ERROR_MESSAGE",
        "Что-то пошло не так. Попробуй выполнить действие ещё раз.",
    )

    if message:
        await message.answer(
            error_text,
            reply_markup=main_menu_keyboard(),
        )

    return True
