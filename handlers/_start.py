from aiogram import Router
from aiogram.filters import Command

router = Router()


@router.message(Command("start"))
async def echo(message):
    return message.answer("Введите название трека или используйте команду\n/help")
