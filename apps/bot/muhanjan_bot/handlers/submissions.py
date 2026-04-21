from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message

from muhanjan_bot import texts
from muhanjan_bot.keyboards.reply import main_menu_keyboard
from muhanjan_bot.services.submissions import (
    build_submission_payload,
    is_message_usable_for_submission,
    send_submission,
)
from muhanjan_bot.services.users import ensure_remote_user, fetch_user_state
from muhanjan_bot.utils.formatters import format_ban_reason, html_safe

router = Router(name="submissions")


@router.message(F.content_type.in_({"text", "photo", "document", "video"}))
async def handle_submission(message: Message) -> None:
    state = await fetch_user_state(message.from_user.id)

    if not state.get("exists"):
        await ensure_remote_user(message)
        state = await fetch_user_state(message.from_user.id)

    if state.get("is_banned"):
        reason_block = texts.BANNED_REASON_BLOCK.format(
            reason=html_safe(format_ban_reason(state.get("ban_reason")))
        )
        await message.answer(
            texts.BANNED_MESSAGE.format(reason_block=reason_block),
            reply_markup=main_menu_keyboard(),
        )
        return

    if not state.get("has_twitch_nickname"):
        await message.answer(texts.NEED_TWITCH_FIRST, reply_markup=main_menu_keyboard())
        return

    if not is_message_usable_for_submission(message):
        await message.answer(texts.EMPTY_SUBMISSION, reply_markup=main_menu_keyboard())
        return

    payload = await build_submission_payload(message.bot, message)
    result = await send_submission(payload)

    if not result.get("ok"):
        detail = (result.get("detail") or "").strip().lower()

        if "twitch" in detail:
            await message.answer(texts.NEED_TWITCH_FIRST, reply_markup=main_menu_keyboard())
            return

        if "заблок" in detail:
            reason_block = texts.BANNED_REASON_BLOCK.format(
                reason=html_safe(format_ban_reason(state.get("ban_reason")))
            )
            await message.answer(
                texts.BANNED_MESSAGE.format(reason_block=reason_block),
                reply_markup=main_menu_keyboard(),
            )
            return

        await message.answer(texts.SUBMISSION_FAILED, reply_markup=main_menu_keyboard())
        return

    status_value = result.get("status")
    if status_value == "approved":
        await message.answer(texts.SUBMISSION_SUCCESS_APPROVED, reply_markup=main_menu_keyboard())
        return

    await message.answer(texts.SUBMISSION_SUCCESS_PENDING, reply_markup=main_menu_keyboard())


@router.message()
async def fallback_message(message: Message) -> None:
    await ensure_remote_user(message)
    await message.answer(texts.FALLBACK_TEXT, reply_markup=main_menu_keyboard())
