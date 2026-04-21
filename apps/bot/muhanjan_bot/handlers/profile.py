from __future__ import annotations

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from muhanjan_bot import texts
from muhanjan_bot.keyboards.reply import main_menu_keyboard
from muhanjan_bot.services.api import BotApiError
from muhanjan_bot.services.users import ensure_remote_user, update_twitch_nickname
from muhanjan_bot.states.profile import ProfileState
from muhanjan_bot.utils.formatters import html_safe

router = Router(name="profile")


@router.message(ProfileState.waiting_twitch)
async def set_twitch(message: Message, state: FSMContext) -> None:
    try:
        await ensure_remote_user(message)
    except BotApiError:
        await message.answer(texts.API_TEMPORARY_UNAVAILABLE, reply_markup=main_menu_keyboard())
        return

    nickname = (message.text or "").strip().lstrip("@")
    if len(nickname) < 3:
        await message.answer(texts.TWITCH_TOO_SHORT, reply_markup=main_menu_keyboard())
        return

    try:
        await update_twitch_nickname(message.from_user.id, nickname)
    except BotApiError:
        await message.answer(texts.API_TEMPORARY_UNAVAILABLE, reply_markup=main_menu_keyboard())
        return

    await state.clear()
    await message.answer(
        texts.TWITCH_UPDATED.format(nickname=html_safe(nickname)),
        reply_markup=main_menu_keyboard(),
    )
