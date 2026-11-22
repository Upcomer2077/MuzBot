from typing import Final

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_i18n import I18nContext

from _logger import LOGGER
from bot.bot import bot
from handlers.modules._subscriptions._unsub.callbacks import UnSubCallback
from infra.dungeon import DM
from localization import L10N

router = Router()


@router.callback_query(UnSubCallback.filter())
async def handle_un_sub(
    callback: CallbackQuery, callback_data: UnSubCallback, i18n: I18nContext
):
    await callback.answer()  # Reset button timer

    AUTHOR_ID: Final[str] = callback_data.author_id

    if len(AUTHOR_ID) == 0:
        LOGGER.error("AUTHOR_ID param len is 0. Check callback data")
        return callback.answer(i18n.get(L10N["subs"].usub_error_generic))
    # --------------
    USER_ID: Final = callback.from_user.id

    await DM.subs.drop_sub(AUTHOR_ID, USER_ID)

    return await bot.send_message(USER_ID, i18n.get(L10N["subs"].usub_success))
