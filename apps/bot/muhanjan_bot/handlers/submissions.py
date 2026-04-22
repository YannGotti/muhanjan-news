from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from muhanjan_bot import texts
from muhanjan_bot.config import settings
from muhanjan_bot.keyboards.inline import submission_preview_keyboard
from muhanjan_bot.keyboards.reply import main_menu_keyboard
from muhanjan_bot.services.api import BotApiError
from muhanjan_bot.services.files import BotFileValidationError
from muhanjan_bot.services.limits import acquire_submission_cooldown, register_submission_message
from muhanjan_bot.services.submissions import (
    build_submission_payload,
    is_message_usable_for_submission,
    send_submission,
)
from muhanjan_bot.services.users import ensure_remote_user, fetch_user_state
from muhanjan_bot.states.submission import SubmissionState
from muhanjan_bot.utils.formatters import format_ban_reason, format_seconds, html_safe

router = Router(name="submissions")

URL_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)


def _extract_links(text: str | None) -> list[str]:
    if not text:
        return []
    return list(dict.fromkeys(URL_RE.findall(text)))


def _truncate(value: str, limit: int = 260) -> str:
    value = value.strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def _format_attachments(payload: dict) -> str:
    attachments = payload.get("attachments") or []
    if not attachments:
        return texts.PREVIEW_NO_ATTACHMENTS

    labels: list[str] = []
    for item in attachments[:6]:
        labels.append(str(item.get("file_type") or "file"))
    if len(attachments) > 6:
        labels.append(f"+{len(attachments) - 6}")
    return ", ".join(labels)


def _preview_summary(payload: dict) -> str:
    message_text = (payload.get("message_text") or "").strip()
    links = _extract_links(message_text)
    text_block = html_safe(_truncate(message_text)) if message_text else texts.PREVIEW_NO_TEXT

    return (
        f"<b>{texts.PREVIEW_TEXT_LABEL}:</b> {text_block}\n"
        f"<b>{texts.PREVIEW_LINKS_LABEL}:</b> {len(links)}\n"
        f"<b>{texts.PREVIEW_ATTACHMENTS_LABEL}:</b> {html_safe(_format_attachments(payload))}"
    )


async def _ensure_submission_permissions(message: Message) -> dict | None:
    try:
        state = await fetch_user_state(message.from_user.id)

        if not state.get("exists"):
            await ensure_remote_user(message)
            state = await fetch_user_state(message.from_user.id)
    except BotApiError:
        await message.answer(texts.API_TEMPORARY_UNAVAILABLE, reply_markup=main_menu_keyboard())
        return None

    if state.get("is_banned"):
        reason_block = texts.BANNED_REASON_BLOCK.format(
            reason=html_safe(format_ban_reason(state.get("ban_reason")))
        )
        await message.answer(
            texts.BANNED_MESSAGE.format(reason_block=reason_block),
            reply_markup=main_menu_keyboard(),
        )
        return None

    if not state.get("has_twitch_nickname"):
        await message.answer(texts.NEED_TWITCH_FIRST, reply_markup=main_menu_keyboard())
        return None

    return state


@router.message(F.content_type.in_({"text", "photo", "document", "video", "audio", "voice", "animation"}))
async def handle_submission(message: Message, state: FSMContext) -> None:
    user_state = await _ensure_submission_permissions(message)
    if user_state is None:
        return

    if not is_message_usable_for_submission(message):
        await message.answer(texts.EMPTY_SUBMISSION, reply_markup=main_menu_keyboard())
        return

    try:
        payload = await build_submission_payload(message.bot, message)
    except BotFileValidationError:
        max_size_mb = max(settings.max_upload_file_size_bytes // (1024 * 1024), 1)
        await message.answer(
            texts.FILE_TOO_LARGE_MESSAGE.format(max_size_mb=max_size_mb),
            reply_markup=main_menu_keyboard(),
        )
        return
    except BotApiError:
        await message.answer(texts.API_TEMPORARY_UNAVAILABLE, reply_markup=main_menu_keyboard())
        return

    await state.set_state(SubmissionState.waiting_confirmation)
    await state.update_data(pending_submission=payload)

    await message.answer(
        texts.SUBMISSION_PREVIEW_HEADER.format(summary=_preview_summary(payload)),
        reply_markup=submission_preview_keyboard(),
    )


@router.callback_query(StateFilter(SubmissionState.waiting_confirmation), F.data == "submission:cancel")
async def cancel_submission_preview(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(texts.SUBMISSION_PREVIEW_CANCELED)


@router.callback_query(StateFilter(SubmissionState.waiting_confirmation), F.data == "submission:confirm")
async def confirm_submission_preview(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    payload = data.get("pending_submission")

    if not payload:
        await state.clear()
        await callback.answer(texts.SUBMISSION_PREVIEW_EXPIRED, show_alert=True)
        return

    if callback.message is None:
        await callback.answer()
        return

    try:
        state_payload = await fetch_user_state(callback.from_user.id)
    except BotApiError:
        await callback.answer()
        await callback.message.answer(texts.API_TEMPORARY_UNAVAILABLE, reply_markup=main_menu_keyboard())
        return

    if state_payload.get("is_banned"):
        reason_block = texts.BANNED_REASON_BLOCK.format(
            reason=html_safe(format_ban_reason(state_payload.get("ban_reason")))
        )
        await callback.answer()
        await callback.message.answer(
            texts.BANNED_MESSAGE.format(reason_block=reason_block),
            reply_markup=main_menu_keyboard(),
        )
        return

    source_message_id = payload.get("source_message_id")
    if source_message_id is not None:
        is_unique_message = await register_submission_message(callback.from_user.id, int(source_message_id))
        if not is_unique_message:
            await state.clear()
            await callback.answer()
            await callback.message.edit_text(texts.SUBMISSION_ALREADY_SENT_MESSAGE)
            return

    allowed, ttl = await acquire_submission_cooldown(callback.from_user.id)
    if not allowed:
        await callback.answer()
        await callback.message.answer(
            texts.RATE_LIMIT_MESSAGE.format(seconds=format_seconds(ttl)),
            reply_markup=main_menu_keyboard(),
        )
        return

    try:
        result = await send_submission(payload)
    except BotApiError:
        await callback.answer()
        await callback.message.answer(texts.API_TEMPORARY_UNAVAILABLE, reply_markup=main_menu_keyboard())
        return

    if not result.get("ok"):
        detail = (result.get("detail") or "").strip().lower()

        if "twitch" in detail:
            await state.clear()
            await callback.answer()
            await callback.message.edit_text(texts.NEED_TWITCH_FIRST)
            return

        if "заблок" in detail:
            reason_block = texts.BANNED_REASON_BLOCK.format(
                reason=html_safe(format_ban_reason(state_payload.get("ban_reason")))
            )
            await state.clear()
            await callback.answer()
            await callback.message.edit_text(texts.BANNED_MESSAGE.format(reason_block=reason_block))
            return

        await callback.answer()
        await callback.message.answer(texts.SUBMISSION_FAILED, reply_markup=main_menu_keyboard())
        return

    await state.clear()
    await callback.answer()

    status_value = result.get("status")
    if status_value == "approved":
        await callback.message.edit_text(texts.SUBMISSION_SUCCESS_APPROVED)
        return

    await callback.message.edit_text(texts.SUBMISSION_SUCCESS_PENDING)


@router.message()
async def fallback_message(message: Message) -> None:
    try:
        await ensure_remote_user(message)
    except BotApiError:
        await message.answer(texts.API_TEMPORARY_UNAVAILABLE, reply_markup=main_menu_keyboard())
        return

    await message.answer(texts.FALLBACK_TEXT, reply_markup=main_menu_keyboard())
