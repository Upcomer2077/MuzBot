from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.commands import COMMANDS, COMSET

router = Router()


@router.message(COMMANDS[COMSET.CANCEL]["backend"])
async def cancel_handler(message: Message, state: FSMContext):

    if await state.get_state() is None:
        return message.answer("Нечего отменять")

    await state.clear()
    await message.answer("❌ Действие отменено")
