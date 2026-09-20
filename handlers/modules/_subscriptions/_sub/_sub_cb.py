from typing import Final

from aiogram import Router
from aiogram.types import CallbackQuery

import bot
from _logger import LOGGER
from action_limiter import AL
from config import SUBSCRIPTION_COOLDOWN_SECS, SUBSCRIPTIONS_PER_LIMIT
from dungeon import DM
from schemas.callbacks import SubCallback
from tools.extract_artist_discography import extract_artist_discography

router = Router()


@router.callback_query(SubCallback.filter())
async def handle_sub(callback: CallbackQuery, callback_data: SubCallback):
    await callback.answer()  # Reset button timer

    AUTHOR_ID: Final[str] = callback_data.author_id

    if len(AUTHOR_ID) == 0:
        LOGGER.error("AUTHOR_ID param len is 0. Check callback data")
        return callback.answer(
            "Что-то пошло не так при попытке подписаться... Повторите попытку"
        )
    # --------------
    USER_ID: Final = callback.from_user.id
    local_author_info = await DM.subs.get_performer_info(AUTHOR_ID)

    if local_author_info:
        return await __subscribe(USER_ID, AUTHOR_ID, local_author_info.name)

    if not AL.is_subscription_allowed(USER_ID):
        return await bot.bot.send_message(
            USER_ID,
            f"Слишком большое число запросов на подписку! Разрешено делать {SUBSCRIPTIONS_PER_LIMIT} запросов в течение {SUBSCRIPTION_COOLDOWN_SECS} секунд",
        )

    AUTHOR_INFO: Final = await extract_artist_discography(AUTHOR_ID)

    ALBUMS = [] if not AUTHOR_INFO["albums"] else AUTHOR_INFO["albums"]["results"]
    SINGLES = [] if not AUTHOR_INFO["singles"] else AUTHOR_INFO["singles"]["results"]
    NAME = AUTHOR_INFO["name"]

    await DM.subs.set_performer_last_release(
        AUTHOR_ID,
        performer_name=NAME,
        last_album_id=ALBUMS[0]["browseId"] if len(ALBUMS) else None,
        last_single_id=SINGLES[0]["browseId"] if len(SINGLES) else None,
    )

    return await __subscribe(USER_ID, AUTHOR_ID, NAME)


async def __subscribe(USER_ID: int, AUTHOR_ID: str, a_name: str):
    await DM.subs.subscribe_to_performer(USER_ID, AUTHOR_ID)
    return await bot.bot.send_message(USER_ID, f"Вы подписались на автора {a_name}")
