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
from config import PAGINATION_ITEMS_PER_PAGE
from dungeon import DM
from handlers.modules._subscriptions._unsub.callbacks import (
    PaginationUSubsArtistsCallback,
    UnSubCallback,
)
from helpers.get_ytm_links import get_browse_link
from helpers.utils import U
from localization import L10N
from schemas.states import TypedState

router = Router()


class _USubscriptionState(StatesGroup):
    first_state = State()


@router.message(COMMANDS[COMSET.UNSUBSCRIBE]["backend"])
async def subscribe(
    message: Message, command: CommandObject, state: FSMContext, i18n: I18nContext
):
    S: Final = TypedState(state)

    performer = command.args
    if not performer:
        await S.set_state(_USubscriptionState.first_state)
        return await message.answer(
            i18n.get(
                L10N["subs"].sub_prompt_performer, cancelcommand=COMSET.CANCEL.value
            )
        )

    await _handler(message, performer, S, i18n)


@router.message(_USubscriptionState.first_state)
async def unsubscribe_step_2(message: Message, state: FSMContext, i18n: I18nContext):
    S: Final = TypedState(state)

    performer = message.text
    if not performer:
        return await message.answer(
            i18n.get(
                L10N["subs"].sub_prompt_performer, cancelcommand=COMSET.CANCEL.value
            )
        )

    await S.clear()
    await _handler(message, performer, S, i18n)


async def _handler(message: Message, performer: str, S: TypedState, i18n: I18nContext):
    ANSWER = await message.answer(i18n.get(L10N["subs"].sub_searching))
    if not message.from_user:
        return await ANSWER.edit_text(i18n.get(L10N["subs"].list_unknown_error))

    USER_ID = message.from_user.id
    subs = await DM.performers.get_artists_by_name(USER_ID, performer)

    if not len(subs):
        return await ANSWER.edit_text(i18n.get(L10N["subs"].usub_not_found))

    content, _nav_markup, _drop_builder, start_idx = U.get_page_content(
        subs, page=0, pag_cb_type=PaginationUSubsArtistsCallback
    )

    builder = InlineKeyboardBuilder()

    text = i18n.get(L10N["subs"].sub_results_title) + "\n"
    for idx, artist in enumerate(content, start=start_idx + 1):
        title = artist.name
        text += f'#{idx}. <a href="{get_browse_link(artist.id)}">{title}</a>\n'
        builder.button(
            text=f"🔕{idx}",
            callback_data=UnSubCallback(author_id=artist.id),
        )

    if len(subs) > PAGINATION_ITEMS_PER_PAGE:
        builder.attach(_nav_markup)
        await S.update_data({"usubs_artists": subs})

    builder.attach(_drop_builder).adjust(3, repeat=True)

    return await ANSWER.edit_text(
        text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML
    )
