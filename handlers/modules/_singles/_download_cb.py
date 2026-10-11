from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext

import bot
from _logger import LOGGER
from action_limiter import AL
from config import (
    MAX_TRACK_DURATION_SECONDS,
    QUERY_DOWNLOAD_LIMIT_SECS,
    TRACKS_PER_LIMIT,
)
from handlers.modules._singles.callbacks import DownloadCallback
from helpers.utils import U
from localization import L10N
from worker import TRACK_PIPELINE
from worker.priorities import DownloadTaskPriorities

router = Router()


@router.callback_query(DownloadCallback.filter())
async def handle_download(
    callback: CallbackQuery, callback_data: DownloadCallback, i18n: I18nContext
):
    await callback.answer()  # Reset button timer

    VIDEO_ID = callback_data.video_id
    IDX = callback_data.idx

    if len(VIDEO_ID) == 0:
        LOGGER.error("Video_id param len is 0. Check callback data")
        return callback.answer(i18n.get(L10N["single"].download_error_generic, idx=IDX))
    # --------------

    ANCHOR_MESSAGE = callback.message or await U.send_anchor_message(
        callback.from_user.id
    )
    ANSWER = await ANCHOR_MESSAGE.answer(i18n.get(L10N["single"].download_processing))
    IS_FROM_INLINE_QUERY = callback.message is None
    CHAT_ID = ANCHOR_MESSAGE.chat.id

    if IS_FROM_INLINE_QUERY and isinstance(ANCHOR_MESSAGE, Message):
        await ANCHOR_MESSAGE.delete()

    track = await U.get_track(VIDEO_ID)
    if not track:
        return ANCHOR_MESSAGE.answer(i18n.get(L10N["single"].download_info_not_found))

    if track.is_too_large:
        return ANSWER.edit_text(
            i18n.get(
                L10N["single"].download_limit_size_duration,
                limit_min=int(MAX_TRACK_DURATION_SECONDS / 60),
            )
        )

    if not AL.is_track_download_allowed(CHAT_ID):
        return ANSWER.edit_text(
            i18n.get(
                L10N["single"].download_limit_rate,
                limit_tracks=TRACKS_PER_LIMIT,
                limit_secs=QUERY_DOWNLOAD_LIMIT_SECS,
            )
        )

    if AL.is_send_action_allowed(CHAT_ID):
        await U.send_action(CHAT_ID)

    if not track.telegram_file_id:
        _, cache = await TRACK_PIPELINE.submit(
            VIDEO_ID,
            track_title=track.title,
            artist=track.artist,
            priority=DownloadTaskPriorities.SINGLE,
        )
        if cache.file_id or cache.is_too_large:
            if cache.is_too_large:
                return ANSWER.edit_text(
                    i18n.get(
                        L10N["single"].download_limit_size_duration,
                        limit_min=int(MAX_TRACK_DURATION_SECONDS / 60),
                    )
                )
            track = await U.get_track(VIDEO_ID, extract_info_from_ytm=False)
            if not (track and track.telegram_file_id):
                return ANCHOR_MESSAGE.answer(
                    i18n.get(L10N["single"].download_info_not_found)
                )

        else:
            return ANSWER.edit_text(
                i18n.get(
                    L10N["single"].download_error_failed,
                    artist=track.artist,
                    title=track.title,
                )
            )

    await bot.bot.send_audio(CHAT_ID, track.telegram_file_id)
    return ANSWER.delete()
