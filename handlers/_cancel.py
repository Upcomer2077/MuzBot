from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_i18n import I18nContext

from bot.commands import COMMANDS, COMSET
from localization import L10N

router = Router()


@router.message(COMMANDS[COMSET.CANCEL]["backend"])
async def cancel_handler(message: Message, state: FSMContext, i18n: I18nContext):

    if await state.get_state() is None:
        return message.answer(i18n.get(L10N["cancel"].cancel_nothing))

    await state.clear()
    await message.answer(i18n.get(L10N["cancel"].cancel_success))
