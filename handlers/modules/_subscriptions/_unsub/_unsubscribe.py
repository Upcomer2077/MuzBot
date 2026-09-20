from typing import Final

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.commands import COMMANDS, COMSET
from config import PAGINATION_ITEMS_PER_PAGE
from dungeon import DM
from helpers.get_ytm_links import get_artist_link
from helpers.utils import U
from schemas.callbacks import UnSubCallback
from schemas.callbacks.pagination import PaginationUSubsArtistsCallback
from schemas.states import TypedState
from schemas.states.subs import USubsArtistsStates

router = Router()


@router.message(COMMANDS[COMSET.UNSUBSCRIBE]["backend"])
async def subscribe(message: Message, command: CommandObject, state: FSMContext):
    S: Final = TypedState(state)

    ANSWER = await message.answer("Ищу исполнителей...")
    if not message.from_user:
        return ANSWER.edit_text("Неизвестная ошибка")
    performer = command.args
    if not performer:
        return ANSWER.edit_text("Не указан исполнитель")

    USER_ID = message.from_user.id
    subs = await DM.subs.get_artists_by_name(USER_ID, performer)

    if not len(subs):
        return ANSWER.edit_text("Указанный исполнитель не найден в ваших подписках")

    content, _nav_markup, _drop_builder, start_idx = U.get_page_content(
        subs, page=0, pag_cb_type=PaginationUSubsArtistsCallback
    )

    builder = InlineKeyboardBuilder()

    text = "Найденные исполнители: \n"
    for idx, artist in enumerate(content, start=start_idx + 1):
        title = artist.name
        text += f'#{idx}. <a href="{get_artist_link(artist.id)}">{title}</a>\n'
        builder.button(
            text=f"🔕{idx}",
            callback_data=UnSubCallback(author_id=artist.id),
        )

    if len(subs) > PAGINATION_ITEMS_PER_PAGE:
        builder.attach(_nav_markup)
        await S.update_data({"usubs_artists": subs})
        await S.set_state(USubsArtistsStates.browsing_results)

    builder.attach(_drop_builder).adjust(3, repeat=True)

    return ANSWER.edit_text(
        text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML
    )
