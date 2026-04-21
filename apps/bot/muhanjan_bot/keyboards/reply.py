from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from muhanjan_bot import texts


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    rows = []
    for row in texts.MAIN_MENU_BUTTONS:
        rows.append([KeyboardButton(text=label) for label in row])

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Выбери действие или отправь материал",
    )
