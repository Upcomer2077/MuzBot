from typing import Final

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from action_limiter import AL
from config import SUBSCRIPTION_COOLDOWN_SECS, SUBSCRIPTIONS_PER_LIMIT
from handlers.modules._albums.callbacks import AlbumsCallback, PaginationAlbums1Callback
from helpers.get_ytm_links import get_browse_link
from helpers.utils import U
from localization import L10N
from schemas.states import TypedState
from tools.types import ArtistsShortInfoDict

router = Router()


@router.callback_query(PaginationAlbums1Callback.filter())
async def process_pagination(
    callback: CallbackQuery,
    callback_data: PaginationAlbums1Callback,
    state: FSMContext,
    i18n: I18nContext,
):
    if not AL.is_subscription_allowed(callback.from_user.id):
        return await callback.answer(
            i18n.get(
                L10N["albums"].alb_limit_rate,
                limit_count=SUBSCRIPTIONS_PER_LIMIT,
                limit_secs=SUBSCRIPTION_COOLDOWN_SECS,
            )
        )
    S: Final = TypedState(state)
    data = await S.get_data()
    artists: list[ArtistsShortInfoDict] | None = data.get(
        "albums_pack", {"artists": []}
    ).get("artists", None)

    if not artists or not len(artists):
        return await callback.answer(
            i18n.get(
                L10N["shared"].too_old_result,
            ),
        )

    target_page = callback_data.page

    content, _nav_markup, _drop_builder, start_idx = U.get_page_content(
        artists, page=target_page, pag_cb_type=PaginationAlbums1Callback, max=0
    )

    builder = InlineKeyboardBuilder()

    text = i18n.get(L10N["albums"].alb_results_title_pag, num=target_page + 1) + "\n"
    for idx, artist in enumerate(content, start=start_idx + 1):
        title = artist["name"]
        text += f'#{idx}. <a href="{get_browse_link(artist["id"])}">{title}</a>\n'
        builder.button(
            text=f"💿{idx}",
            callback_data=AlbumsCallback(author_id=artist["id"]),
        )

    builder.attach(_nav_markup).attach(_drop_builder).adjust(3, repeat=True)

    message = callback.message
    if message and isinstance(message, Message):
        await message.edit_text(
            text=text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML
        )

    await callback.answer()
