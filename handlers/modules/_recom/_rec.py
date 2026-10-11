from typing import Final

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext
from tortoise.expressions import Q

import bot
from action_limiter import AL
from bot.commands import COMSET
from config import PAGINATION_ITEMS_PER_PAGE, SEARCH_COOLDOWN_SECS, SEARCH_PER_LIMIT
from dungeon import DM
from dungeon.models import TrackCache
from handlers.modules._recom.callbacks import PaginationRecCallback
from handlers.modules._singles.callbacks import DownloadCallback
from helpers.utils import U
from localization import L10N
from schemas.states import TypedState
from tools.get_watch_pl import get_watch_pl

router = Router()


@router.message(F.audio)
async def handle_audio(message: Message, state: FSMContext, i18n: I18nContext):
    S: Final = TypedState(state)
    if not message.from_user:
        return await message.answer(i18n.get(L10N["recommendations"].rec_error_unknown))

    USER_ID: Final = message.from_user.id

    if not AL.is_search_allowed(USER_ID):
        return message.answer(
            i18n.get(
                L10N["recommendations"].rec_limit_rate,
                limit_count=SEARCH_PER_LIMIT,
                limit_secs=SEARCH_COOLDOWN_SECS,
            )
        )
    STATUS_MESSAGE = await message.answer(
        i18n.get(L10N["recommendations"].rec_searching)
    )

    audio = message.audio
    if not audio:
        return await STATUS_MESSAGE.edit_text(
            i18n.get(L10N["recommendations"].rec_error_invalid_file)
        )

    # TODO: file unique id?
    file_id = audio.file_id
    file_name = audio.title
    file_performer = audio.performer

    track = await TrackCache.filter(
        Q(telegram_file_id=file_id) | Q(title=file_name, artist=file_performer)
    ).first()

    if not track:
        bot_info = await bot.Bot.get_me(bot.bot)
        botname = f"@{bot_info.username}" if bot_info else "этого бота"
        return await STATUS_MESSAGE.edit_text(
            i18n.get(
                L10N["recommendations"].rec_error_unrecognized_forward,
                botname=botname,
                helpcommand=COMSET.HELP.value,
            )
        )

    watch_pl = await get_watch_pl(track.video_id)
    if not watch_pl:
        return await STATUS_MESSAGE.edit_text(
            i18n.get(L10N["recommendations"].rec_error_not_found)
        )

    await DM.tracks.enslave_bulk(watch_pl)

    content, _nav_markup, _drop_builder, start_idx = U.get_page_content(
        watch_pl, page=0, pag_cb_type=PaginationRecCallback
    )

    builder = InlineKeyboardBuilder()
    text = i18n.get(L10N["recommendations"].rec_results_title) + "\n\n"
    for i, video in enumerate(content, start=start_idx + 1):
        v_id = video["video_id"]
        title = video["title"]
        duration = video["duration"]
        artist = video["artist"]
        text += f"#{i}. {artist} — {title} [{duration}]\n"

        builder.button(
            text=f"⬇️ {i}",
            callback_data=DownloadCallback(video_id=v_id, idx=str(i)),
        )

    if len(watch_pl) > PAGINATION_ITEMS_PER_PAGE:
        builder.attach(_nav_markup)
        await S.update_data({"rec_result": watch_pl})

    builder.attach(_drop_builder).adjust(3, repeat=True)

    await STATUS_MESSAGE.edit_text(
        text, reply_markup=builder.as_markup(), parse_mode=None
    )
