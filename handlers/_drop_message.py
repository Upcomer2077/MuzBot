from aiogram import F, Router, types

router = Router()


@router.callback_query(F.data.startswith("drop_m"))
async def drop_search_message(callback: types.CallbackQuery):
    await callback.answer()
    if isinstance(callback.message, types.Message):
        await callback.message.delete()
