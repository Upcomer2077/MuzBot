from typing import Final

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from action_limiter import AL
from bot.commands import COMMANDS, COMSET
from config import (
    PAGINATION_ITEMS_PER_PAGE,
    SUBSCRIPTION_COOLDOWN_SECS,
    SUBSCRIPTIONS_PER_LIMIT,
)
from handlers.modules._catalog.callbacks import (
    CatalogCallback,
    PaginationSingles1Callback,
)
from helpers.get_ytm_links import get_browse_link
from helpers.prettify_incoming_query import prettify_incoming_query
from helpers.utils import U
from schemas.states import TypedState
from tools.search_artists import search_artists_in_ytm

router = Router()


class _CatalogState(StatesGroup):
    first_state = State()


@router.message(COMMANDS[COMSET.CATALOG]["backend"])
async def get_artists(message: Message, command: CommandObject, state: FSMContext):
    if not AL.is_subscription_allowed(message.chat.id):
        return await message.answer(
            f"Достигнут лимит запросов каталогов: {SUBSCRIPTIONS_PER_LIMIT} авторов за {SUBSCRIPTION_COOLDOWN_SECS} секунд",
        )
    S: Final = TypedState(state)

    performer = command.args
    if not performer:
        await S.set_state(_CatalogState.first_state)
        return await message.answer(
            f"Укажите исполнителя или используйте /{COMSET.CANCEL.value}"
        )

    await _handler(message, performer, S)


@router.message(_CatalogState.first_state)
async def get_artists_step_2(message: Message, state: FSMContext):
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
        artists, page=0, pag_cb_type=PaginationSingles1Callback
    )

    builder = InlineKeyboardBuilder()

    text = "Найденные исполнители: \n"
    for idx, artist in enumerate(content, start=start_idx + 1):
        title = artist["name"]
        text += f'#{idx}. <a href="{get_browse_link(artist["id"])}">{title}</a>\n'
        builder.button(
            text=f"💿{idx}",
            callback_data=CatalogCallback(author_id=artist["id"]),
        )

    if len(artists) > PAGINATION_ITEMS_PER_PAGE:
        builder.attach(_nav_markup)
        await S.update_data({"singles_pack": {"artists": artists}})

    builder.attach(_drop_builder).adjust(3, repeat=True)

    return await ANSWER.edit_text(
        text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML
    )
