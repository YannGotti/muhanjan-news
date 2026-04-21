from aiogram.fsm.state import State, StatesGroup


class ProfileState(StatesGroup):
    waiting_twitch = State()
