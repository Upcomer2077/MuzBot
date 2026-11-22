from typing import TypedDict, cast

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StateType

from infra.dungeon.models import Albums, Singles, YTPerformers
from infra.dungeon.types.subs import GetUserSubsResult
from infra.tools.types import ArtistsShortInfoDict, SearchResultDict


class StateData(TypedDict, total=False):
    subs_list: list[GetUserSubsResult]
    search_result: list[SearchResultDict]
    rec_result: list[SearchResultDict]
    subs_artists: list[ArtistsShortInfoDict]
    usubs_artists: list[YTPerformers]
    singles_pack: _PlaylistPack[Singles]
    albums_pack: _PlaylistPack[Albums]


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


class _PlaylistPack[T](TypedDict, total=False):
    artists: list[ArtistsShortInfoDict]
    entities: list[T]
