import asyncio
from functools import reduce
from typing import Sequence

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import FSInputFile, Message
from aiogram.utils.media_group import MediaGroupBuilder, MediaType

import bot
from _logger import LOGGER
from dungeon import DM
from dungeon.models import TrackCache
from helpers import pull_data_from_cache
from helpers.cache_reducer import split_by_cache
from helpers.prepare_audio_file_to_send import prepare_audio_file_to_send
from tools.extract_playlist_info import extract_playlist_info

router = Router()


@router.message(Command("playlist"))
async def playlist1(message: Message, command: CommandObject):
    await message.answer("Загружаю")
    if not message.from_user:
        return message.answer("Неизвестная ошибка")

    user_id = message.from_user.id

    args = command.args
    if not args:
        return message.answer("Отсутствует ссылка на видео")
    link = args
    LOGGER.info("Playlist")
    videos = await extract_playlist_info(link)
    if videos is None:
        return print("Хуйня")

    await DM.enslave_bulk(videos)

    tracks_info = await DM.summon_slaves([i["video_id"] for i in videos])
    if not tracks_info:
        raise

    # ===============
    # WORK IN PROGRESS
    r = reduce(split_by_cache, tracks_info.values(), {"cached": [], "missing": []})
    wip_tracks = [track for track in tracks_info.values() if track.is_work_in_progress]
    if len(wip_tracks) > 0:
        timeout = 60
        while len(wip_tracks) > 0 and timeout > 0:
            timeout -= 6
            await asyncio.sleep(6)
            tracks = await DM.summon_slaves([i.video_id for i in wip_tracks])
            wip_tracks = [
                track for track in tracks.values() if track.is_work_in_progress
            ]
        else:
            if timeout <= 0:
                LOGGER.warn("Awaiting of playlist mutex took too long (>= 60sec)")
            tracks_info = await DM.summon_slaves([i["video_id"] for i in videos])

    # ==============
    mg_builder = MediaGroupBuilder()
    media_group_cached: list[Sequence[MediaType]] = []

    group_count = 0
    for t in r["cached"]:
        if t.telegram_file_id:
            mg_builder.add_audio(media=t.telegram_file_id)
            group_count += 1
        if group_count >= 10:
            media_group_cached.append(mg_builder.build())
            mg_builder = MediaGroupBuilder()
            group_count = 0
    else:
        media_group_cached.append(mg_builder.build())
        mg_builder = MediaGroupBuilder()
        group_count = 0

    LOGGER.info(f"Sending cached: ({len(media_group_cached)} groups)")
    for t in media_group_cached:
        if len(t):
            await bot.bot.send_media_group(user_id, list(t), disable_notification=True)
            await asyncio.sleep(1)

    # ==========
    non_cached_tracks = r["missing"]

    await DM.fisting([i.video_id for i in non_cached_tracks], is_work_in_progress=True)

    tasks = [
        pull_data_from_cache.pull_data_from_cache(v.video_id) for v in non_cached_tracks
    ]

    cache_data_list = await asyncio.gather(*tasks, return_exceptions=False)

    audio_non_cached: list[tuple[TrackCache, FSInputFile, FSInputFile | None]] = []
    unable_to_download_id: list[str] = []
    # ==========

    for t in cache_data_list:
        (
            a,
            b,
        ) = t
        if not b:
            unable_to_download_id.append(a)
            continue

        # fsize = get_file_size(Path(t["audio_path"]))
        audio_file, thumbnail = prepare_audio_file_to_send(b)

        current_track = tracks_info[b["_video_id"]]
        audio_non_cached.append((current_track, audio_file, thumbnail))
    LOGGER.info(f"Media group count: {len(audio_non_cached) + len(media_group_cached)}")

    LOGGER.info(f"Sending non-cached: ({len(audio_non_cached)} audios)")
    for t in audio_non_cached:
        a, a_file, thumbnail = t
        sent_message: Message = await bot.bot.send_audio(
            user_id,
            a_file,
            thumbnail=thumbnail,
            title=a.title,
            performer=a.artist,
            disable_notification=True,
        )
        if sent_message.audio:
            await DM.fisting(
                a.video_id,
                telegram_file_id=sent_message.audio.file_id,
                is_work_in_progress=False,
            )

        await asyncio.sleep(0.5)

    text = "Не удалось отправить треки:\n"
    for idx, u in enumerate(unable_to_download_id, 1):
        track = tracks_info[u]
        text += f"#{idx}. {track.artist} - {track.title}\n"

    if len(unable_to_download_id):
        await bot.bot.send_message(
            user_id, f"{text}Повторите попытку или скачайте отдельно"
        )
    LOGGER.info("Playlist done")
