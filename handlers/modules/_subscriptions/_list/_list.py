from typing import Final

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from bot.commands import COMMANDS, COMSET
from config import PAGINATION_ITEMS_PER_PAGE
from dungeon import DM
from dungeon.types.subs import GetUserSubsResult
from handlers.modules._subscriptions._list.callbacks import PaginationSubsListCallback
from handlers.modules._subscriptions._unsub.callbacks import UnSubCallback
from helpers.get_ytm_links import get_browse_link
from helpers.utils import U
from localization import L10N
from schemas.states import TypedState

router = Router()


@router.message(COMMANDS[COMSET.SUBSCRIPTIONS]["backend"])
async def subs_list(
    message: Message, state: FSMContext, command: CommandObject, i18n: I18nContext
):
    S: Final = TypedState(state)
    ANSWER = await message.answer(i18n.get(L10N["subs"].list_searching))
    if not message.from_user:
        return ANSWER.edit_text(i18n.get(L10N["subs"].list_unknown_error))
    USER_ID = message.from_user.id
    ARGS: Final = command.args
    subs: list[GetUserSubsResult] = []

    async for batch in DM.subs.get_user_subscriptions(
        USER_ID, batch_size=1, s_query=ARGS
    ):
        subs += batch

    if not len(subs):
        if ARGS:
            return ANSWER.edit_text(i18n.get(L10N["subs"].list_not_found_query))
        return ANSWER.edit_text(i18n.get(L10N["subs"].list_empty))

    builder = InlineKeyboardBuilder()

    content, _nav_markup, drop_builder, start_idx = U.get_page_content(
        subs, page=0, pag_cb_type=PaginationSubsListCallback, max=0
    )

    text = f"{i18n.get(L10N['subs'].list_title)}\n\n"
    for idx, artist in enumerate(content, start=start_idx + 1):
        title = artist["name"]
        text += (
            f'#{idx}. <a href="{get_browse_link(artist["performer_id"])}">{title}</a>\n'
        )
        builder.button(
            text=f"🔕{idx}",
            callback_data=UnSubCallback(author_id=artist["performer_id"]),
        )

    if len(subs) > PAGINATION_ITEMS_PER_PAGE:
        builder.attach(_nav_markup)
        await S.update_data({"subs_list": subs})

    builder.attach(drop_builder).adjust(3, repeat=True)

    return ANSWER.edit_text(
        text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML
    )
