from aiogram.fsm.state import State, StatesGroup


class SubmissionState(StatesGroup):
    waiting_confirmation = State()
