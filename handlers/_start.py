from aiogram import Router
from aiogram.types import Message
from aiogram_i18n import I18nContext

from bot.commands import COMMANDS, COMSET
from dungeon import DM
from localization import L10N

router = Router()


@router.message(COMMANDS[COMSET.START]["backend"])
async def echo(message: Message, i18n: I18nContext):
    await message.answer(i18n.get(L10N["start"].start))
    if message.from_user:
        await DM.subs.toggle_user_subscriptions(message.from_user.id, False)
