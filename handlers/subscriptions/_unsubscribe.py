from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from dungeon import DM
from schemas.callbacks import DropCallback, UnSubCallback

router = Router()


@router.message(Command("usub"))
async def subscribe(message: Message, command: CommandObject):
    ANSWER = await message.answer("Ищу исполнителей...")
    if not message.from_user:
        return ANSWER.edit_text("Неизвестная ошибка")
    performer = command.args
    if not performer:
        return ANSWER.edit_text("Не указан исполнитель")

    USER_ID = message.from_user.id
    subs = await DM.get_artists_by_name(USER_ID, performer)

    if not len(subs):
        return ANSWER.edit_text("Указанный исполнитель не найден в ваших подписках")

    builder = InlineKeyboardBuilder()

    text = "Найденные исполнители: \n"
    for idx, artist in enumerate(subs, start=1):
        title = artist.name
        text += f'#{idx}. <a href="https://music.youtube.com/browse/{artist.id}">{title}</a>\n'
        builder.button(
            text=f"🔕{idx}",
            callback_data=UnSubCallback(author_id=artist.id),
        )
    text += "\nОтписаться?"

    builder.button(
        text="❌",
        callback_data=DropCallback(),
    ).adjust(3, repeat=True)

    return ANSWER.edit_text(
        text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML
    )
