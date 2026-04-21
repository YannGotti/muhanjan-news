from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from muhanjan_bot import texts
from muhanjan_bot.keyboards.reply import main_menu_keyboard
from muhanjan_bot.services.api import BotApiError
from muhanjan_bot.services.users import ensure_remote_user, fetch_user_state
from muhanjan_bot.states.profile import ProfileState
from muhanjan_bot.utils.formatters import format_ban_reason, html_safe

router = Router(name="menu")


def _status_message(state: dict) -> str:
    sending = "недоступна" if state.get("is_banned") else "доступна"
    ban_line = ""
    if state.get("is_banned"):
        ban_line = texts.BAN_LINE.format(reason=html_safe(format_ban_reason(state.get("ban_reason"))))
    return texts.STATUS_TEMPLATE.format(
        twitch=html_safe(state.get("twitch_nickname") or "не указан"),
        sending=sending,
        ban_line=ban_line,
    )


async def _send_main_screen(message: Message, state: FSMContext) -> None:
    try:
        data = await ensure_remote_user(message)

        if data.get("is_banned"):
            user_state = await fetch_user_state(message.from_user.id)
            reason_text = texts.BANNED_REASON_BLOCK.format(
                reason=html_safe(format_ban_reason(user_state.get("ban_reason")))
            )
            await message.answer(
                texts.BANNED_MESSAGE.format(reason_block=reason_text),
                reply_markup=main_menu_keyboard(),
            )
            return

        if not data.get("has_twitch_nickname"):
            await state.set_state(ProfileState.waiting_twitch)
            await message.answer(
                f"{texts.START_GREETING}\n\n{texts.FIRST_TWITCH_REQUEST}",
                reply_markup=main_menu_keyboard(),
            )
            return

        await state.clear()
        await message.answer(
            f"{texts.START_GREETING}\n\n{texts.SEND_HINT_TEXT}",
            reply_markup=main_menu_keyboard(),
        )
    except BotApiError:
        await message.answer(texts.API_TEMPORARY_UNAVAILABLE, reply_markup=main_menu_keyboard())


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext) -> None:
    await _send_main_screen(message, state)


@router.message(Command("menu"))
async def menu_command(message: Message, state: FSMContext) -> None:
    await _send_main_screen(message, state)


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    try:
        await ensure_remote_user(message)
    except BotApiError:
        await message.answer(texts.API_TEMPORARY_UNAVAILABLE, reply_markup=main_menu_keyboard())
        return

    await message.answer(texts.HELP_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("status"))
async def status_command(message: Message) -> None:
    try:
        await ensure_remote_user(message)
        state = await fetch_user_state(message.from_user.id)
    except BotApiError:
        await message.answer(texts.PROFILE_TEMPORARY_UNAVAILABLE, reply_markup=main_menu_keyboard())
        return

    if not state.get("exists"):
        await message.answer(texts.PROFILE_TEMPORARY_UNAVAILABLE, reply_markup=main_menu_keyboard())
        return

    await message.answer(_status_message(state), reply_markup=main_menu_keyboard())


@router.message(Command("twitch"))
async def twitch_command(message: Message, state: FSMContext) -> None:
    try:
        await ensure_remote_user(message)
    except BotApiError:
        await message.answer(texts.API_TEMPORARY_UNAVAILABLE, reply_markup=main_menu_keyboard())
        return

    await state.set_state(ProfileState.waiting_twitch)
    await message.answer(texts.ASK_NEW_TWITCH, reply_markup=main_menu_keyboard())


@router.message(lambda message: (message.text or "").strip() == texts.MENU_HELP)
async def help_button(message: Message) -> None:
    await help_command(message)


@router.message(lambda message: (message.text or "").strip() == texts.MENU_SEND)
async def send_button(message: Message) -> None:
    try:
        await ensure_remote_user(message)
    except BotApiError:
        await message.answer(texts.API_TEMPORARY_UNAVAILABLE, reply_markup=main_menu_keyboard())
        return

    await message.answer(texts.SEND_HINT_TEXT, reply_markup=main_menu_keyboard())


@router.message(lambda message: (message.text or "").strip() == texts.MENU_STATUS)
async def status_button(message: Message) -> None:
    await status_command(message)


@router.message(lambda message: (message.text or "").strip() == texts.MENU_CHANGE_TWITCH)
async def change_twitch_button(message: Message, state: FSMContext) -> None:
    try:
        await ensure_remote_user(message)
    except BotApiError:
        await message.answer(texts.API_TEMPORARY_UNAVAILABLE, reply_markup=main_menu_keyboard())
        return

    await state.set_state(ProfileState.waiting_twitch)
    await message.answer(texts.ASK_NEW_TWITCH, reply_markup=main_menu_keyboard())


@router.message(lambda message: (message.text or "").strip() == texts.MENU_MENU)
async def show_menu_button(message: Message, state: FSMContext) -> None:
    await _send_main_screen(message, state)
