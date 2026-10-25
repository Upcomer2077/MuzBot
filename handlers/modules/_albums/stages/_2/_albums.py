from typing import Final

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

import bot
from _logger import LOGGER
from action_limiter import AL
from config import CATALOG_COOLDOWN_SECS, CATALOG_PER_LIMIT, PAGINATION_ITEMS_PER_PAGE
from dungeon import DM
from handlers.modules._albums.callbacks import (
    AlbumsCallback,
    PaginationAlbums2Callback,
    ShowAlbumPlaylistContentCallback,
)
from helpers.get_ytm_links import get_browse_link
from helpers.utils import U
from localization import L10N
from schemas.states import TypedState
from tools.extract_artist_discography import extract_artist_discography

router = Router()


@router.callback_query(AlbumsCallback.filter())
async def get_albums_list(
    callback: CallbackQuery,
    state: FSMContext,
    callback_data: AlbumsCallback,
    i18n: I18nContext,
):
    await callback.answer()
    USER_ID = callback.from_user.id
    if not AL.is_catalog_action_allowed(USER_ID):
        return await bot.bot.send_message(
            USER_ID,
            i18n.get(
                L10N["albums"].alb_action_limit_rate,
                limit_count=CATALOG_PER_LIMIT,
                limit_secs=CATALOG_COOLDOWN_SECS,
            ),
        )

    S: Final = TypedState(state)
    ANSWER = await bot.bot.send_message(
        USER_ID, i18n.get(L10N["albums"].alb_searching_generic)
    )
    AUTHOR_ID = callback_data.author_id

    releases = await DM.performers.get_artist_albums(AUTHOR_ID)
    LOGGER.debug(
        f"Found info about artist {AUTHOR_ID} albums: {len(releases) if releases else None}"
    )
    if not releases:
        res = await extract_artist_discography(AUTHOR_ID, top_only=False)

        if not res:
            LOGGER.error(
                f"Cannot extract performer {AUTHOR_ID} releases on albums/stage/2"
            )
            return await ANSWER.edit_text(i18n.get(L10N["albums"].alb_error_failed))
        await DM.performers.set_performer_releases_v2(AUTHOR_ID, info=res)

        if not res["albums"] or not len(res["albums"]):
            LOGGER.debug(f"Performer {res['name']} has no albums")
            return await ANSWER.edit_text(i18n.get(L10N["albums"].alb_pl_has_no_albums))

        releases = await DM.performers.get_artist_albums(AUTHOR_ID)
        LOGGER.debug(
            f"2 Found info about artist {AUTHOR_ID} albums: {len(releases) if releases else None}"
        )
        if not releases:
            LOGGER.error(f"Cannot set performer {AUTHOR_ID} releases on albums/stage/2")
            return await ANSWER.edit_text(i18n.get(L10N["albums"].alb_error_failed))

    albums = releases

    if not albums:
        return await ANSWER.edit_text(i18n.get(L10N["albums"].alb_no_albums))

    content, _nav_markup, _drop_builder, start_idx = U.get_page_content(
        albums, page=0, pag_cb_type=PaginationAlbums2Callback
    )

    builder = InlineKeyboardBuilder()

    text = i18n.get(L10N["albums"].alb_albums_title) + "\n"
    for idx, album in enumerate(content, start=start_idx + 1):
        title = album.playlist.title
        text += f'#{idx}. <a href="{get_browse_link(album.browse_id)}">{title}</a>\n'
        builder.button(
            text=f"🎶{idx}",
            callback_data=ShowAlbumPlaylistContentCallback(
                playlist_id=album.playlist.playlist_id
            ),
        )

    if len(albums) > PAGINATION_ITEMS_PER_PAGE:
        builder.attach(_nav_markup)
        await S.update_data({"albums_pack": {"entities": albums}})

    builder.attach(_drop_builder).adjust(3, repeat=True)

    return await ANSWER.edit_text(
        text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML
    )
