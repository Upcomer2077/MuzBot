from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from dungeon import DM

router = Router()


@router.message(Command("start"))
async def echo(message: Message):
    await message.answer(
        "Введите название трека и/или автора. Используйте\n/help для получения инструкции"
    )
    if message.from_user:
        await DM.subs.toggle_user_subscriptions(message.from_user.id, False)
