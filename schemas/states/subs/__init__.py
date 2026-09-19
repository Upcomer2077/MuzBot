from aiogram.fsm.state import State, StatesGroup


class SubsListStates(StatesGroup):
    browsing_results = State()


class SubsArtistsStates(StatesGroup):
    browsing_results = State()


class USubsArtistsStates(StatesGroup):
    browsing_results = State()
