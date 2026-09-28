from typing import Final

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import bot
from _logger import LOGGER
from action_limiter import AL
from config import CATALOG_COOLDOWN_SECS, CATALOG_PER_LIMIT, PAGINATION_ITEMS_PER_PAGE
from dungeon import DM
from handlers.modules._catalog.callbacks import (
    CatalogCallback,
    PaginationSingles2Callback,
    ShowSinglePlaylistContentCallback,
)
from helpers.get_ytm_links import get_browse_link
from helpers.utils import U
from schemas.states import TypedState
from tools.extract_artist_discography import extract_artist_discography

router = Router()


@router.callback_query(CatalogCallback.filter())
async def get_singles_list(
    callback: CallbackQuery, state: FSMContext, callback_data: CatalogCallback
):
    await callback.answer()
    USER_ID = callback.from_user.id
    if not AL.is_catalog_action_allowed(USER_ID):
        return await bot.bot.send_message(
            USER_ID,
            f"Достигнут лимит запросов каталога: {CATALOG_PER_LIMIT} плейлистов за {CATALOG_COOLDOWN_SECS} секунд",
        )

    S: Final = TypedState(state)
    ANSWER = await bot.bot.send_message(callback.from_user.id, "Ищу...")
    AUTHOR_ID = callback_data.author_id
    releases = await DM.performers.get_artist_singles(AUTHOR_ID)
    LOGGER.debug(
        f"Found info about artist {AUTHOR_ID} singles: {len(releases) if releases else None}"
    )
    if not releases:
        res = await extract_artist_discography(AUTHOR_ID, top_only=False)
        if not res:
            LOGGER.error(
                f"Cannot extract performer {AUTHOR_ID} releases on catalog/stage/2"
            )
            return await ANSWER.edit_text(
                "Не удалось выполнить запрос. Повторите попытку"
            )
        await DM.performers.set_performer_releases_v2(AUTHOR_ID, info=res)

        releases = await DM.performers.get_artist_singles(AUTHOR_ID)
        LOGGER.debug(
            f"2 Found info about artist {AUTHOR_ID} singles: {len(releases) if releases else None}"
        )
        if not releases:
            LOGGER.error(
                f"Cannot set performer {AUTHOR_ID} releases on catalog/stage/2"
            )
            return await ANSWER.edit_text(
                "Не удалось выполнить запрос. Повторите попытку"
            )

    singles = releases

    if not singles:
        return await ANSWER.edit_text("У исполнителя нет выпусков")

    content, _nav_markup, _drop_builder, start_idx = U.get_page_content(
        singles, page=0, pag_cb_type=PaginationSingles2Callback
    )

    builder = InlineKeyboardBuilder()

    text = "Найденные выпуски: \n"
    for idx, album in enumerate(content, start=start_idx + 1):
        title = album.playlist.title
        text += f'#{idx}. <a href="{get_browse_link(album.browse_id)}">{title}</a>\n'
        builder.button(
            text=f"🎶{idx}",
            callback_data=ShowSinglePlaylistContentCallback(
                playlist_id=album.playlist.playlist_id
            ),
        )

    if len(singles) > PAGINATION_ITEMS_PER_PAGE:
        builder.attach(_nav_markup)
        await S.update_data({"singles_pack": {"entities": singles}})

    builder.attach(_drop_builder).adjust(3, repeat=True)

    return await ANSWER.edit_text(
        text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML
    )
