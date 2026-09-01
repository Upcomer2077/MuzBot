from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from helpers.utils import U
from schemas.callbacks.search_pagination import PaginationCallback
from schemas.states.search import SearchStates

router = Router()


@router.callback_query(SearchStates.browsing_results, PaginationCallback.filter())
async def process_pagination(
    callback: CallbackQuery, callback_data: PaginationCallback, state: FSMContext
):
    data = await state.get_data()
    search_result = data.get("search_result", [])

    if not search_result:
        await callback.answer(
            "Результаты поиска устарели. Повторите поиск.", show_alert=True
        )
        return

    target_page = callback_data.page
    text, reply_markup = U.get_page_content(search_result, page=target_page)

    message = callback.message
    if message and isinstance(message, Message):
        await message.edit_text(text=text, reply_markup=reply_markup, parse_mode=None)

    await callback.answer()
