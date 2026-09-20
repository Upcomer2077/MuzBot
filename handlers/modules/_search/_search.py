from typing import Final

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from action_limiter import AL
from config import PAGINATION_ITEMS_PER_PAGE
from dungeon import DM
from helpers.prettify_incoming_query import prettify_incoming_query
from helpers.utils import U
from schemas.callbacks import DownloadCallback
from schemas.callbacks.pagination import PaginationSearchCallback
from schemas.states import TypedState
from schemas.states.search import SearchStates
from tools.search import search_in_ytm
from tools.types import YoutubeSearchResultDict

router = Router()


@router.message()
async def get_list(message: Message, state: FSMContext):
    S: Final = TypedState(state)
    QUERY = message.text
    if QUERY is None or message.from_user is None:
        return None

    USER_ID: Final = message.from_user.id

    if not AL.is_search_allowed(USER_ID):
        return message.answer("Слишком много запросов!")

    clean_text = prettify_incoming_query(QUERY)

    if len(clean_text) == 0:
        return None
    STATUS_MESSAGE = await message.answer("🔍 Ищу варианты...")
    search_result: list[YoutubeSearchResultDict] = await search_in_ytm(QUERY, 27)

    if len(search_result) == 0:
        return STATUS_MESSAGE.edit_text("404 🤷")

    await DM.tracks.enslave_bulk(search_result)

    content, _nav_markup, _drop_builder, start_idx = U.get_page_content(
        search_result, page=0, pag_cb_type=PaginationSearchCallback
    )

    builder = InlineKeyboardBuilder()
    text = "Найденные варианты:\n\n"
    for i, video in enumerate(content, start=start_idx + 1):
        v_id = video["video_id"]
        title = video["title"]
        duration = video["duration"]
        artist = video["artist"]
        text += f"#{i}. {artist} — {title} [{duration}]\n"

        builder.button(
            text=f"⬇️ {i}",
            callback_data=DownloadCallback(video_id=v_id, idx=str(i)),
        )
    # TODO: search in video category
    # if not (end_idx < len(search_result) and end_idx < _MAX_ITEMS):
    #     text += "\nНе нашли что искали? Попробуйте добавить -v в конце запроса"

    if len(search_result) > PAGINATION_ITEMS_PER_PAGE:
        builder.attach(_nav_markup)
        await S.update_data({"search_result": search_result})
        await S.set_state(SearchStates.browsing_results)

    builder.attach(_drop_builder).adjust(3, repeat=True)

    await STATUS_MESSAGE.edit_text(
        text, reply_markup=builder.as_markup(), parse_mode=None
    )
