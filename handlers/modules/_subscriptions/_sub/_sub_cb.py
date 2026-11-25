from typing import Final

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_i18n import I18nContext

from bot.bot import bot
from config import SUBSCRIPTION_COOLDOWN_SECS, SUBSCRIPTIONS_PER_LIMIT
from handlers.modules._subscriptions._sub.callbacks import SubCallback
from infra.action_limiter import AL
from infra.tools.MusicTools import MT
from interfaces.idatabase import IDataBase
from interfaces.ilogger import ILogger
from localization import L10N

router = Router()


@router.callback_query(SubCallback.filter())
async def handle_sub(
    callback: CallbackQuery,
    callback_data: SubCallback,
    i18n: I18nContext,
    logger: ILogger,
    DM: IDataBase,
):
    await callback.answer()  # Reset button timer

    AUTHOR_ID: Final[str] = callback_data.author_id

    if len(AUTHOR_ID) == 0:
        logger.error("AUTHOR_ID param len is 0. Check callback data")
        return callback.answer(i18n.get(L10N["subs"].sub_error_generic))
    # --------------
    USER_ID: Final = callback.from_user.id
    local_author_info = await DM.performers.get_performer_info(AUTHOR_ID)

    if local_author_info:
        return await __subscribe(USER_ID, AUTHOR_ID, local_author_info.name, i18n, DM)

    if not AL.is_subscription_allowed(USER_ID):
        return await bot.send_message(
            USER_ID,
            i18n.get(
                L10N["subs"].sub_limit_exceeded,
                limit=SUBSCRIPTIONS_PER_LIMIT,
                cooldown=SUBSCRIPTION_COOLDOWN_SECS,
            ),
        )

    AUTHOR_INFO: Final = await MT.extract_artist_discography(AUTHOR_ID)
    if not AUTHOR_INFO:
        return callback.answer(i18n.get(L10N["subs"].sub_error_generic))

    ALBUMS = [] if not AUTHOR_INFO["albums"] else AUTHOR_INFO["albums"]
    SINGLES = [] if not AUTHOR_INFO["singles"] else AUTHOR_INFO["singles"]
    NAME = AUTHOR_INFO["name"]

    await DM.subs.set_performer_last_release(
        AUTHOR_ID,
        performer_name=NAME,
        last_album_id=ALBUMS[0]["browseId"] if len(ALBUMS) else None,
        last_single_id=SINGLES[0]["browseId"] if len(SINGLES) else None,
    )

    return await __subscribe(USER_ID, AUTHOR_ID, AUTHOR_INFO["name"], i18n, DM)


async def __subscribe(
    USER_ID: int, AUTHOR_ID: str, a_name: str, i18n: I18nContext, DM: IDataBase
):
    await DM.subs.subscribe_to_performer(USER_ID, AUTHOR_ID)
    return await bot.send_message(
        USER_ID, i18n.get(L10N["subs"].sub_success, name=a_name)
    )
