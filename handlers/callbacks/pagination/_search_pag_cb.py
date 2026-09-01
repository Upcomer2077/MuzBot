from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from helpers.utils import U
from schemas.callbacks.search_pagination import PaginationCallback

router = Router()


@router.callback_query(PaginationCallback.filter())
async def process_pagination(
    callback: CallbackQuery, callback_data: PaginationCallback, state: FSMContext
):
    data = await state.get_data()
    search_result = data.get("search_result", [])

    if not state or not data or not search_result or not len(search_result):
        return await callback.answer(
            "Результаты поиска устарели. Повторите поиск.", show_alert=True
        )

    target_page = callback_data.page
    text, reply_markup = U.get_page_content(search_result, page=target_page)

    message = callback.message
    if message and isinstance(message, Message):
        await message.edit_text(text=text, reply_markup=reply_markup, parse_mode=None)

    await callback.answer()
