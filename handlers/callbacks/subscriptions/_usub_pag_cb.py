from typing import Final

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from helpers.get_ytm_video_link import get_artist_link
from helpers.utils import U
from schemas.callbacks import UnSubCallback
from schemas.callbacks.pagination import PaginationUSubsArtistsCallback
from schemas.states import TypedState

router = Router()


@router.callback_query(PaginationUSubsArtistsCallback.filter())
async def process_pagination(
    callback: CallbackQuery,
    callback_data: PaginationUSubsArtistsCallback,
    state: FSMContext,
):
    S: Final = TypedState(state)
    data = await S.get_data()
    subs = data.get("subs_artists", [])

    if not subs or not len(subs):
        return await callback.answer(
            "Результаты поиска устарели. Повторите поиск.", show_alert=True
        )

    target_page = callback_data.page

    content, _nav_markup, _drop_builder, start_idx = U.get_page_content(
        subs, page=target_page, pag_cb_type=PaginationUSubsArtistsCallback, max=0
    )

    builder = InlineKeyboardBuilder()

    text = f"Найденные исполнители (Страница {target_page + 1}):\n\n"
    for idx, artist in enumerate(content, start=start_idx + 1):
        title = artist["name"]
        text += f'#{idx}. <a href="{get_artist_link(artist["id"])}">{title}</a>\n'
        builder.button(
            text=f"🔔{idx}",
            callback_data=UnSubCallback(author_id=artist["id"]),
        )

    builder.attach(_nav_markup).attach(_drop_builder).adjust(3, repeat=True)

    message = callback.message
    if message and isinstance(message, Message):
        await message.edit_text(
            text=text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML
        )

    await callback.answer()
