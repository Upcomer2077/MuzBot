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
from dungeon.types.subs import GetUserSubsResult
from helpers.get_ytm_links import get_artist_link
from helpers.utils import U
from schemas.callbacks import UnSubCallback
from schemas.callbacks.pagination import PaginationSubsListCallback
from schemas.states import TypedState
from schemas.states.subs import SubsListStates

router = Router()


@router.message(COMMANDS[COMSET.SUBSCRIPTIONS]["backend"])
async def subs_list(message: Message, state: FSMContext, command: CommandObject):
    S: Final = TypedState(state)
    ANSWER = await message.answer("Ищу исполнителей...")
    if not message.from_user:
        return ANSWER.edit_text("Неизвестная ошибка")
    USER_ID = message.from_user.id
    ARGS: Final = command.args
    subs: list[GetUserSubsResult] = []

    async for batch in DM.subs.get_user_subscriptions(
        USER_ID, batch_size=1, s_query=ARGS
    ):
        subs += batch

    if not len(subs):
        if ARGS:
            return ANSWER.edit_text("Подписок по данному запросу не найдено")
        return ANSWER.edit_text("Нет активных подписок")

    builder = InlineKeyboardBuilder()

    content, _nav_markup, drop_builder, start_idx = U.get_page_content(
        subs, page=0, pag_cb_type=PaginationSubsListCallback, max=0
    )

    text = "Ваши подписки:\n\n"
    for idx, artist in enumerate(content, start=start_idx + 1):
        title = artist["name"]
        text += (
            f'#{idx}. <a href="{get_artist_link(artist["performer_id"])}">{title}</a>\n'
        )
        builder.button(
            text=f"🔕{idx}",
            callback_data=UnSubCallback(author_id=artist["performer_id"]),
        )

    if len(subs) > PAGINATION_ITEMS_PER_PAGE:
        builder.attach(_nav_markup)
        await S.update_data({"subs_list": subs})
        await S.set_state(SubsListStates.browsing_results)

    builder.attach(drop_builder).adjust(3, repeat=True)

    return ANSWER.edit_text(
        text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML
    )
