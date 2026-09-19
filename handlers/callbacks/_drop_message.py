from aiogram import Router, types
from aiogram.exceptions import TelegramBadRequest

from schemas.callbacks import DropCallback

router = Router()


@router.callback_query(DropCallback.filter())
async def drop_search_message(callback: types.CallbackQuery):
    await callback.answer()
    if isinstance(callback.message, types.Message):
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass
