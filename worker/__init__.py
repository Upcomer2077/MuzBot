import asyncio
from collections.abc import Sequence
from functools import reduce

from aiogram.types import FSInputFile, Message
from aiogram.utils.media_group import MediaGroupBuilder, MediaType

import bot
from _logger import LOGGER
from config import CHANNEL_STORAGE_ID
from dungeon import DM
from dungeon.models import TrackCache
from helpers.cache_reducer import split_by_cache
from helpers.chunker import chunked_downloader
from helpers.prepare_audio_file_to_send import prepare_audio_file_to_send
from worker.worker import PlaylistQueueManager


async def playlist_worker_loop():
    """Фоновый воркер, который обрабатывает плейлисты строго по одному."""
    LOGGER.info("🤖 Фоновый воркер очереди плейлистов успешно запущен!")

    while True:
        # Ждем задачу. Если очередь пуста, код здесь засыпает, не загружая CPU
        # task = await PLAYLIST_QUEUE.next_task()
        async with PLAYLIST_QUEUE as task:
            LOGGER.info(f"🚀 Воркер взял в работу плейлист {task.playlist_id}")

            tracks_info = await DM.summon_slaves([i["video_id"] for i in task.videos])
            if not tracks_info:
                raise

            # ===============
            # WORK IN PROGRESS
            r = reduce(
                split_by_cache, tracks_info.values(), {"cached": [], "missing": []}
            )
            wip_tracks = [
                track for track in tracks_info.values() if track.is_work_in_progress
            ]
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
                        LOGGER.warn(
                            "Awaiting of playlist mutex took too long (>= 60sec)"
                        )
                    tracks_info = await DM.summon_slaves(
                        [i["video_id"] for i in task.videos]
                    )

            non_cached_tracks = r["missing"]

            await DM.fisting(
                [i.video_id for i in non_cached_tracks], is_work_in_progress=True
            )

            unable_to_download_id: list[str] = []
            async for cache_data_list in chunked_downloader(non_cached_tracks):
                audio_non_cached: list[
                    tuple[TrackCache, FSInputFile, FSInputFile | None]
                ] = []
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
                # LOGGER.info(
                #     f"Media group count: {len(audio_non_cached) + len(media_group_cached)}"
                # )

                for t in audio_non_cached:
                    a, a_file, thumbnail = t
                    sent_message: Message = await bot.bot.send_audio(
                        CHANNEL_STORAGE_ID,
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
                # ==============

            mg_builder = MediaGroupBuilder()
            media_group_cached: list[Sequence[MediaType]] = []
            tracks_info = await DM.summon_slaves_from_playlist(task.playlist_id)

            group_count = 0
            for t in tracks_info.values():
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
                    await bot.bot.send_media_group(
                        task.user_id, list(t), disable_notification=True
                    )
                    await asyncio.sleep(1)

            text = "Не удалось отправить треки:\n"
            for idx, u in enumerate(unable_to_download_id, 1):
                track = tracks_info[u]
                text += f"#{idx}. {track.artist} - {track.title}\n"

            if len(unable_to_download_id):
                await bot.bot.send_message(
                    task.user_id, f"{text}Повторите попытку или скачайте отдельно"
                )
            LOGGER.info("Playlist done")

        # ==========

        # Обязательно освобождаем место в реестре очереди, чтобы сдвинуть остальных пользователей
        LOGGER.info(f"🏁 Воркер завершил задачу для пользователя {task.user_id}")
        await asyncio.sleep(10)


PLAYLIST_QUEUE = PlaylistQueueManager()
