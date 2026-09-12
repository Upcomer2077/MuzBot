from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from dungeon import DM
from helpers.prettify_incoming_query import prettify_incoming_query
from helpers.utils import U
from schemas.dicts import YoutubeSearchResultDict
from schemas.states.search import SearchStates
from tools.search import search_in_ytm

router = Router()


@router.message()
async def get_list(message: Message, state: FSMContext):
    await state.clear()
    QUERY = message.text
    if QUERY is None:
        return None
    clean_text = prettify_incoming_query(QUERY)

    if len(clean_text) == 0:
        return None
    STATUS_MESSAGE = await message.answer("🔍 Ищу варианты...")
    search_result: list[YoutubeSearchResultDict] = await search_in_ytm(QUERY, 27)

    if len(search_result) == 0:
        return STATUS_MESSAGE.edit_text("404 🤷")

    await state.update_data(search_result=search_result)
    await state.set_state(SearchStates.browsing_results)

    await DM.tracks.enslave_bulk(search_result)

    text, reply_markup = U.get_page_content(search_result, page=0)

    await STATUS_MESSAGE.edit_text(text, reply_markup=reply_markup, parse_mode=None)
