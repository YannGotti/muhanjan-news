from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from muhanjan_bot import texts


def submission_preview_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=texts.PREVIEW_CONFIRM, callback_data="submission:confirm"),
                InlineKeyboardButton(text=texts.PREVIEW_CANCEL, callback_data="submission:cancel"),
            ]
        ]
    )
