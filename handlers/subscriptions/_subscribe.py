from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from helpers.prettify_incoming_query import prettify_incoming_query
from schemas.callbacks import DropCallback, SubCallback
from tools.search_artists import search_artists_in_ytm

router = Router()


@router.message(Command("sub"))
async def subscribe(message: Message, command: CommandObject):
    ANSWER = await message.answer("Ищу исполнителей...")
    if not message.from_user:
        return ANSWER.edit_text("Неизвестная ошибка")
    performer = command.args
    if not performer:
        return ANSWER.edit_text("Не указан исполнитель")

    performer = prettify_incoming_query(performer)

    artists = await search_artists_in_ytm(performer)
    builder = InlineKeyboardBuilder()

    text = "Найденные исполнители: \n"
    for idx, artist in enumerate(artists, start=1):
        title = artist["name"]
        text += f'#{idx}. <a href="https://music.youtube.com/browse/{artist["id"]}">{title}</a>\n'
        builder.button(
            text=f"🔔{idx}",
            callback_data=SubCallback(author_id=artist["id"]),
        )
    text += "\nПодписаться?"

    builder.button(
        text="❌",
        callback_data=DropCallback(),
    ).adjust(3, repeat=True)

    return ANSWER.edit_text(
        text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML
    )
