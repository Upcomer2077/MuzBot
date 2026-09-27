from typing import Final

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from action_limiter import AL
from config import CATALOG_COOLDOWN_SECS, CATALOG_PER_LIMIT
from dungeon.models import Singles
from handlers.modules._catalog.callbacks import (
    PaginationSingles2Callback,
    ShowSinglePlaylistContentCallback,
)
from helpers.get_ytm_links import get_browse_link
from helpers.utils import U
from schemas.states import TypedState

router = Router()


@router.callback_query(PaginationSingles2Callback.filter())
async def process_pagination(
    callback: CallbackQuery,
    callback_data: PaginationSingles2Callback,
    state: FSMContext,
):
    USER_ID = callback.from_user.id
    if not AL.is_catalog_action_allowed(USER_ID):
        return await callback.answer(
            f"Достигнут лимит запросов каталога: {CATALOG_PER_LIMIT} плейлистов за {CATALOG_COOLDOWN_SECS} секунд",
        )
    S: Final = TypedState(state)
    data = await S.get_data()
    artists: list[Singles] | None = data.get("singles_pack", {"entities": []}).get(
        "entities", None
    )

    if not artists or not len(artists):
        return await callback.answer(
            "Результаты поиска устарели. Повторите поиск.", show_alert=True
        )

    target_page = callback_data.page

    content, _nav_markup, _drop_builder, start_idx = U.get_page_content(
        artists, page=target_page, pag_cb_type=PaginationSingles2Callback, max=0
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

    builder.attach(_nav_markup).attach(_drop_builder).adjust(3, repeat=True)

    message = callback.message
    if message and isinstance(message, Message):
        await message.edit_text(
            text=text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML
        )

    await callback.answer()
