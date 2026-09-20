from typing import Final

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from helpers.utils import U
from schemas.callbacks import DownloadCallback
from schemas.callbacks.pagination import PaginationSearchCallback
from schemas.states import TypedState

router = Router()


@router.callback_query(PaginationSearchCallback.filter())
async def process_pagination(
    callback: CallbackQuery, callback_data: PaginationSearchCallback, state: FSMContext
):
    S: Final = TypedState(state)
    data = await S.get_data()
    search_result = data.get("search_result", [])

    if not search_result or not len(search_result):
        return await callback.answer(
            "Результаты поиска устарели. Повторите поиск.", show_alert=True
        )

    target_page = callback_data.page

    content, _nav_markup, _drop_markup, start_idx = U.get_page_content(
        search_result, page=target_page, pag_cb_type=PaginationSearchCallback
    )

    builder = InlineKeyboardBuilder()

    text = f"Найденные варианты (Страница {target_page + 1}):\n\n"
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

    builder.attach(_nav_markup).attach(_drop_markup).adjust(3, repeat=True)

    message = callback.message
    if message and isinstance(message, Message):
        await message.edit_text(
            text=text, reply_markup=builder.as_markup(), parse_mode=None
        )

    await callback.answer()
