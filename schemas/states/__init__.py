from typing import TypedDict, cast

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StateType

from dungeon.models import YTPerformers
from schemas.database.types import GetUserSubsResult
from schemas.dicts import YoutubeSearchResultDict
from schemas.dicts.artist import ArtistsShortInfoDict


class StateData(TypedDict, total=False):
    subs_list: list[GetUserSubsResult]
    search_result: list[YoutubeSearchResultDict]
    subs_artists: list[ArtistsShortInfoDict]
    usubs_artists: list[YTPerformers]


class TypedState:
    def __init__(self, state: FSMContext):
        self._state = state

    async def get_data(self) -> StateData:
        data = await self._state.get_data()
        return cast(StateData, data)

    async def update_data(self, data: StateData | None = None) -> StateData:
        return cast(StateData, await self._state.update_data(data))

    async def set_state(self, state: StateType):
        return await self._state.set_state(state)

    async def clear(self) -> None:
        await self._state.clear()
