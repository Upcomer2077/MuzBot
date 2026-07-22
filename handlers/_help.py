from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import bot

router = Router()


@router.message(Command("help"))
async def help(message: Message):
    bot_info = await bot.Bot.get_me(bot.bot)
    text = (
        ""
        "Введите запрос для поиска трека.\n"
        "Если трек не найден - попробуйте ввести более точный запрос.\n"
        "Случается, что трек всё равно не находится. Если вы убеждены, что он есть в базе "
        "[music.youtube.com](https://music.youtube.com/) (это обязательно, никакие другие ссылки не сработают)"
        " - введите команду "
        "`/force` и через пробел вставьте *ссылку* на видео.\n"
        "```Пример: /force https://music.youtube.com/watch?v=qdCU4ReBROc```"
        f"\nДоступен inline-режим. Напишите в любом чате @{bot_info.username or 'username_бота'} <трек>"
    )

    return message.answer(text, parse_mode="Markdown")
