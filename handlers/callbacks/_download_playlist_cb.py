import asyncio
from collections.abc import Sequence
from typing import NamedTuple

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.media_group import MediaGroupBuilder, MediaType

import bot
from _logger import LOGGER
from action_limiter import AL
from config import PLAYLIST_DOWNLOAD_COOLDOWN_SECS
from dungeon import DM
from helpers.utils import U
from tools.extract_playlist_info import extract_playlist_info
from type import DownloadPlaylistCallback
from worker import TRACK_PIPELINE

router = Router()


class _UnableToDownload(NamedTuple):
    v_id: str
    is_too_large: bool


@router.callback_query(DownloadPlaylistCallback.filter())
async def handle_playlist_download(
    callback: CallbackQuery, callback_data: DownloadPlaylistCallback
):
    await callback.answer("Загружаю... Это займет время.")

    USER_ID = callback.from_user.id
    PLAYLIST_ID = callback_data.playlist_id

    if len(PLAYLIST_ID) == 0:
        LOGGER.error("Video_id param len is 0. Check callback data")
        return callback.answer(
            "Что-то пошло не так при загрузке плейлиста... Повторите попытку"
        )

    if not AL.is_playlist_download_allowed(USER_ID):
        # TODO
        return await bot.bot.send_message(
            USER_ID,
            f"Достигнут лимит скачивания плейлистов в {PLAYLIST_DOWNLOAD_COOLDOWN_SECS} секунд",
        )

    if AL.is_send_action_allowed(USER_ID):
        await U.send_action(USER_ID)

    tracks_info = await DM.summon_slaves_from_playlist(PLAYLIST_ID)

    if not tracks_info:
        r = await extract_playlist_info(PLAYLIST_ID)
        if not r:
            return bot.bot.send_message(USER_ID, "404 🤷")
        (playlist_info, videos) = r
        await DM.add_playlist_and_tracks(playlist_info, videos)
        tracks_info = await DM.summon_slaves_from_playlist(PLAYLIST_ID)
        if not tracks_info:
            LOGGER.error(
                f"Cannot extract info about playlist {PLAYLIST_ID} in playlist_cb"
            )
            return bot.bot.send_message(
                USER_ID, "Неизвестная ошибка. Повторите попытку."
            )

    tasks = [
        TRACK_PIPELINE.submit(v.video_id, track_title=v.title, artist=v.artist)
        for v in tracks_info.values()
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
    tracks_info = await DM.summon_slaves_from_playlist(PLAYLIST_ID)

    if not tracks_info:
        LOGGER.error(f"Can not find info about playlist {PLAYLIST_ID} in worker loop.")
        return bot.bot.send_message(
            USER_ID, "Не удалось скачать плейлист. Повторите попытку."
        )

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
    else:
        media_group_cached.append(mg_builder.build())

    for t in media_group_cached:
        if len(t):
            await bot.bot.send_media_group(USER_ID, list(t), disable_notification=True)
            await asyncio.sleep(1)

    if len(unable_to_download):
        text = "Не удалось отправить треки:\n"
        for idx, u in enumerate(unable_to_download, 1):
            track = tracks_info[u.v_id]
            is_too_large_text = ": трек слишком большой, скачать не выйдет."
            text += f"#{idx}. {track.artist} - {track.title}{is_too_large_text if u.is_too_large else ''}\n"

        await bot.bot.send_message(USER_ID, f"{text}")
