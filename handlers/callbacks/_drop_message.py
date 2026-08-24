from aiogram import Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext

from schemas.callbacks import DropCallback
from schemas.states.search import SearchStates

router = Router()


@router.callback_query(SearchStates.browsing_results, DropCallback.filter())
async def drop_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    if isinstance(callback.message, types.Message):
        await callback.message.delete()


@router.callback_query(DropCallback.filter())
async def drop_search_message(callback: types.CallbackQuery):
    await callback.answer()
    if isinstance(callback.message, types.Message):
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass
