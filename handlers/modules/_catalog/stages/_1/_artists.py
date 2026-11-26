from typing import Final

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

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
from helpers.get_page_content import get_page_content
from helpers.get_ytm_links import get_browse_link
from helpers.prettify_incoming_query import prettify_incoming_query
from infra.tools.MusicTools import MT
from interfaces.ilimiter import IActionLimiter
from localization import L10N
from schemas.states import TypedState

router = Router()


class _CatalogState(StatesGroup):
    first_state = State()


@router.message(COMMANDS[COMSET.CATALOG]["backend"])
async def get_artists(
    message: Message,
    command: CommandObject,
    state: FSMContext,
    i18n: I18nContext,
    AL: IActionLimiter,
):
    if not AL.is_subscription_allowed(message.chat.id):
        return await message.answer(
            i18n.get(
                L10N["catalog"].cat_limit_rate,
                limit_count=SUBSCRIPTIONS_PER_LIMIT,
                limit_secs=SUBSCRIPTION_COOLDOWN_SECS,
            )
        )
    S: Final = TypedState(state)

    performer = command.args
    if not performer:
        await S.set_state(_CatalogState.first_state)
        return await message.answer(
            i18n.get(
                L10N["catalog"].cat_prompt_performer, cancelcommand=COMSET.CANCEL.value
            )
        )

    await _handler(message, performer, S, i18n)


@router.message(_CatalogState.first_state)
async def get_artists_step_2(message: Message, state: FSMContext, i18n: I18nContext):
    S: Final = TypedState(state)

    performer = message.text
    if not performer:
        return await message.answer(
            i18n.get(
                L10N["catalog"].cat_prompt_performer, cancelcommand=COMSET.CANCEL.value
            )
        )

    await S.clear()
    await _handler(message, performer, S, i18n)


async def _handler(message: Message, performer: str, S: TypedState, i18n: I18nContext):
    ANSWER = await message.answer(i18n.get(L10N["catalog"].cat_searching))

    performer = prettify_incoming_query(performer)

    artists = await MT.search_artists_in(performer)

    if not len(artists):
        return await ANSWER.edit_text(i18n.get(L10N["catalog"].cat_not_found))

    content, _nav_markup, _drop_builder, start_idx = get_page_content(
        artists, page=0, pag_cb_type=PaginationSingles1Callback
    )

    builder = InlineKeyboardBuilder()

    text = i18n.get(L10N["catalog"].cat_results_title) + "\n"
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
