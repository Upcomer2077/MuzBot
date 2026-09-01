from aiogram.fsm.state import State, StatesGroup


class SearchStates(StatesGroup):
    browsing_results = State()
