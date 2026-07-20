from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("help"))
async def help(message: Message):
    text = (
        ""
        "Введите запрос для поиска трека.\n"
        "Если трек не найден - попробуйте ввести более точный запрос.\n"
        "Случается, что трек всё равно не находится. Если вы убеждены, что он есть в базе "
        "[music.youtube.com](https://music.youtube.com/) (это обязательно, никакие другие ссылки не сработают)"
        " - введите команду "
        "`/force` и через пробел вставьте *ссылку* на видео.\n"
        "Пример: `/force https://music.youtube.com/watch?v=qdCU4ReBROc`"
    )

    return message.answer(text, parse_mode="Markdown")
