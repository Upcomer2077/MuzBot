from typing import Final

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.commands import COMMANDS, COMSET
from config import PAGINATION_ITEMS_PER_PAGE
from helpers.get_ytm_links import get_artist_link
from helpers.prettify_incoming_query import prettify_incoming_query
from helpers.utils import U
from schemas.callbacks import SubCallback
from schemas.callbacks.pagination import PaginationSubsArtistsCallback
from schemas.states import TypedState
from schemas.states.subs import SubsArtistsStates
from tools.search_artists import search_artists_in_ytm

router = Router()


class _SubscriptionState(StatesGroup):
    first_state = State()


@router.message(COMMANDS[COMSET.SUBSCRIBE]["backend"])
async def subscribe(message: Message, command: CommandObject, state: FSMContext):
    S: Final = TypedState(state)

    performer = command.args
    if not performer:
        await S.set_state(_SubscriptionState.first_state)
        return await message.answer(
            f"Укажите исполнителя или используйте /{COMSET.CANCEL.value}"
        )

    await _handler(message, performer, S)


@router.message(_SubscriptionState.first_state)
async def subscribe_step_2(message: Message, state: FSMContext):
    S: Final = TypedState(state)

    performer = message.text
    if not performer:
        return await message.answer(
            f"Укажите исполнителя или используйте /{COMSET.CANCEL.value}"
        )

    await S.clear()
    await _handler(message, performer, S)


async def _handler(message: Message, performer: str, S: TypedState):
    ANSWER = await message.answer("Ищу исполнителей...")

    performer = prettify_incoming_query(performer)

    artists = await search_artists_in_ytm(performer)

    if not len(artists):
        return await ANSWER.edit_text("Указанный исполнитель не найден")

    content, _nav_markup, _drop_builder, start_idx = U.get_page_content(
        artists, page=0, pag_cb_type=PaginationSubsArtistsCallback
    )

    builder = InlineKeyboardBuilder()

    text = "Найденные исполнители: \n"
    for idx, artist in enumerate(content, start=start_idx + 1):
        title = artist["name"]
        text += f'#{idx}. <a href="{get_artist_link(artist["id"])}">{title}</a>\n'
        builder.button(
            text=f"🔔{idx}",
            callback_data=SubCallback(author_id=artist["id"]),
        )

    if len(artists) > PAGINATION_ITEMS_PER_PAGE:
        builder.attach(_nav_markup)
        await S.update_data({"subs_artists": artists})
        await S.set_state(SubsArtistsStates.browsing_results)

    builder.attach(_drop_builder).adjust(3, repeat=True)

    return await ANSWER.edit_text(
        text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML
    )
