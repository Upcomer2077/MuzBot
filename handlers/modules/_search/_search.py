from typing import Final

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from action_limiter import AL
from config import PAGINATION_ITEMS_PER_PAGE, SEARCH_COOLDOWN_SECS, SEARCH_PER_LIMIT
from dungeon import DM
from handlers.modules._search.callbacks import PaginationSearchCallback
from handlers.modules._singles.callbacks import DownloadCallback
from helpers.prettify_incoming_query import prettify_incoming_query
from helpers.utils import U
from localization import L10N
from schemas.states import TypedState
from tools.search import search_in_ytm
from tools.types import YoutubeSearchResultDict

router = Router()


@router.message()
async def get_list(message: Message, state: FSMContext, i18n: I18nContext):
    S: Final = TypedState(state)
    QUERY = message.text
    if QUERY is None or message.from_user is None:
        return None

    USER_ID: Final = message.from_user.id

    if not AL.is_search_allowed(USER_ID):
        return message.answer(
            i18n.get(
                L10N["search"].search_limit_rate,
                limit_count=SEARCH_PER_LIMIT,
                limit_secs=SEARCH_COOLDOWN_SECS,
            )
        )

    clean_text = prettify_incoming_query(QUERY)

    if len(clean_text) == 0:
        return None
    STATUS_MESSAGE = await message.answer(i18n.get(L10N["search"].search_searching))
    search_result: list[YoutubeSearchResultDict] = await search_in_ytm(QUERY, 27)

    if len(search_result) == 0:
        return STATUS_MESSAGE.edit_text(i18n.get(L10N["search"].search_not_found))

    await DM.tracks.enslave_bulk(search_result)

    content, _nav_markup, _drop_builder, start_idx = U.get_page_content(
        search_result, page=0, pag_cb_type=PaginationSearchCallback
    )

    builder = InlineKeyboardBuilder()
    text = i18n.get(L10N["search"].search_results_title) + "\n\n"
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

    if len(search_result) > PAGINATION_ITEMS_PER_PAGE:
        builder.attach(_nav_markup)
        await S.update_data({"search_result": search_result})

    builder.attach(_drop_builder).adjust(3, repeat=True)

    await STATUS_MESSAGE.edit_text(
        text, reply_markup=builder.as_markup(), parse_mode=None
    )
