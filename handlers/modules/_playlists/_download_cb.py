import asyncio
from collections.abc import Sequence
from typing import NamedTuple

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.media_group import MediaGroupBuilder, MediaType
from aiogram_i18n import I18nContext

from bot.bot import bot
from config import PLAYLIST_DOWNLOAD_COOLDOWN_SECS, PLAYLIST_MAX_TRACKS, PLAYLISTS_LIMIT
from handlers.modules._playlists.callbacks import DownloadPlaylistCallback
from helpers.telegram.send_action import send_action
from infra.tools.MusicTools import MT
from interfaces.idatabase import IDataBase
from interfaces.ilimiter import IActionLimiter
from interfaces.ilogger import ILogger
from interfaces.iworkerpipe import IWorkerPipeline
from interfaces.iworkerpipe.priorities import DownloadTaskPriorities
from localization import L10N

router = Router()


class _UnableToDownload(NamedTuple):
    v_id: str
    is_too_large: bool


@router.callback_query(DownloadPlaylistCallback.filter())
async def handle_playlist_download(
    callback: CallbackQuery,
    callback_data: DownloadPlaylistCallback,
    i18n: I18nContext,
    logger: ILogger,
    DM: IDataBase,
    TRACK_PIPELINE: IWorkerPipeline,
    AL: IActionLimiter,
):
    await callback.answer()

    USER_ID = callback.from_user.id
    PLAYLIST_ID = callback_data.playlist_id
    ANSWER = await bot.send_message(USER_ID, i18n.get(L10N["playlist"].pl_downloading))

    if len(PLAYLIST_ID) == 0:
        logger.error("Video_id param len is 0. Check callback data")
        return ANSWER.edit_text(i18n.get(L10N["playlist"].pl_download_error_generic))

    if not AL.is_playlist_download_allowed(USER_ID):
        return ANSWER.edit_text(
            i18n.get(
                L10N["playlist"].pl_download_limit_rate,
                limit_playlists=PLAYLISTS_LIMIT,
                limit_secs=PLAYLIST_DOWNLOAD_COOLDOWN_SECS,
            )
        )

    if AL.is_send_action_allowed(USER_ID):
        await send_action(USER_ID)

    tracks_info = await DM.playlists.summon_slaves_from_playlist(
        PLAYLIST_ID, PLAYLIST_MAX_TRACKS or None
    )

    if not tracks_info:
        r = await MT.extract_playlist_info(PLAYLIST_ID)
        if not r:
            return ANSWER.edit_text(i18n.get(L10N["playlist"].pl_error_not_found))
        (playlist_info, videos) = r
        await DM.playlists.add_playlist_and_tracks(playlist_info, videos)
        tracks_info = await DM.playlists.summon_slaves_from_playlist(
            PLAYLIST_ID, PLAYLIST_MAX_TRACKS or None
        )
        if not tracks_info:
            logger.error(
                f"Cannot extract info about playlist {PLAYLIST_ID} in playlist_cb"
            )
            return ANSWER.edit_text(
                i18n.get(L10N["playlist"].pl_download_error_unknown)
            )

    tasks = [
        TRACK_PIPELINE.submit(
            v.video_id,
            track_title=v.title,
            artist=v.artist,
            priority=DownloadTaskPriorities.ALBUM,
        )
        for v in list(tracks_info.values())
        if v.telegram_file_id is None and not v.is_too_large
    ]

    fresh_pulled = await asyncio.gather(*tasks)
    unable_to_download: list[_UnableToDownload] = []
    for t in fresh_pulled:
        v_id, cache = t
        file_id, is_too_large, is_error = cache
        if not file_id or is_too_large or is_error:
            unable_to_download.append(_UnableToDownload(v_id, is_too_large))
            continue

    mg_builder = MediaGroupBuilder()
    media_group_cached: list[Sequence[MediaType]] = []
    tracks_info = await DM.playlists.summon_slaves_from_playlist(
        PLAYLIST_ID, PLAYLIST_MAX_TRACKS or None
    )

    if not tracks_info:
        logger.error(f"Can not find info about playlist {PLAYLIST_ID} in worker loop.")
        return ANSWER.edit_text(i18n.get(L10N["playlist"].pl_error_db_failed))

    group_count = 0
    for t in tracks_info.values():
        if t.is_too_large:
            unable_to_download.append(_UnableToDownload(t.video_id, True))
        if t.telegram_file_id:
            mg_builder.add_audio(media=t.telegram_file_id)
            group_count += 1
        if group_count >= 10:
            media_group_cached.append(mg_builder.build())
            mg_builder = MediaGroupBuilder()
            group_count = 0
    media_group_cached.append(mg_builder.build())

    for t in media_group_cached:
        if len(t):
            await bot.send_media_group(USER_ID, list(t), disable_notification=True)
            await asyncio.sleep(1)

    and_more = 0
    if len(unable_to_download):
        text = i18n.get(L10N["playlist"].pl_download_failed_title) + "\n"
        for idx, u in enumerate(unable_to_download, 1):
            track = tracks_info[u.v_id]
            is_too_large_text = i18n.get(L10N["playlist"].pl_download_failed_too_large)
            new_line = f"#{idx}. {track.artist} - {track.title}{is_too_large_text if u.is_too_large else ''}\n"
            if len(text) + len(new_line) > 4000:
                and_more += 1
                continue
            text += new_line

        if and_more:
            text += i18n.get(L10N["playlist"].pl_and_more, count=and_more)

        await bot.send_message(USER_ID, f"{text}")

    await ANSWER.delete()
