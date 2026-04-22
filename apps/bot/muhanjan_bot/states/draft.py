from aiogram.fsm.state import State, StatesGroup


class DraftState(StatesGroup):
    waiting_text_append = State()
