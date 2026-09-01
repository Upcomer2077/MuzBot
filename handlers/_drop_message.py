from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from schemas.states.search import SearchStates

router = Router()


@router.callback_query(SearchStates.browsing_results, F.data.startswith("drop_m"))
async def drop_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    if isinstance(callback.message, types.Message):
        await callback.message.delete()


@router.callback_query(F.data.startswith("drop_m"))
async def drop_search_message(callback: types.CallbackQuery):
    await callback.answer()
    if isinstance(callback.message, types.Message):
        await callback.message.delete()
