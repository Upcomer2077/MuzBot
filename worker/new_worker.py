import asyncio
from dataclasses import dataclass, field
from typing import NoReturn

from aiogram.exceptions import TelegramNetworkError

import bot
from _logger import LOGGER
from config import CHANNEL_STORAGE_ID, CPU_POOL, WORKER_CORES_COUNT
from dungeon import DM
from helpers import prepare_audio_file_to_send
from overlord import COLD
from schemas.tuples.worker import DownloadResult
from tools.download import download_from_ytm
from type import TrackDirContentDict

F = asyncio.Future[tuple[str, DownloadResult]]


@dataclass(slots=True)
class _DownloadTask:
    video_id: str
    track_title: str
    artist: str
    future: F = field(default_factory=asyncio.Future)


class WorkerPipe:
    def __init__(self):
        self._queue: asyncio.Queue[_DownloadTask] = asyncio.Queue()
        self._active_downloads: dict[str, list[F]] = {}
        self._pool_semaphore = asyncio.Semaphore(WORKER_CORES_COUNT)
        self._send_semaphore = asyncio.Semaphore(2)
        self._disk_space_semaphore = asyncio.Semaphore(30)
        self._worker_task: asyncio.Task | None = None

    def start(self):
        self._worker_task = asyncio.create_task(self._worker_loop())

    def stop(self):
        if self._worker_task:
            self._worker_task.cancel()
        LOGGER.debug("Worker loop stopped.")

    async def submit(self, video_id: str, *, track_title: str, artist: str):
        """Entry point. Puts task to worker loop
        Returns:
            tuple:
                v_id: video identifier

                cache: (File id, is too large, is error)

        """
        if video_id in self._active_downloads:
            LOGGER.debug(f"🔗 Already downloading {video_id}. Queued...")
            fut: F = asyncio.Future()
            self._active_downloads[video_id].append(fut)
            return await fut

        LOGGER.debug(f"Appending download task to worker queue: {video_id}")
        task = _DownloadTask(video_id=video_id, track_title=track_title, artist=artist)
        self._active_downloads[video_id] = [task.future]

        await self._queue.put(task)
        return await task.future

    async def _execute_download_task(self, v_id: str, *, title: str, artist: str):
        """Autonomous worker task. Downloads music and sends it to telegram cache-channel"""
        is_too_large = False
        is_error = False
        file_id = None
        success = False
        cache = None

        async with self._disk_space_semaphore:
            async with self._pool_semaphore:
                try:
                    LOGGER.debug(f"Starting worker task on {v_id}")
                    loop = asyncio.get_event_loop()
                    success = await loop.run_in_executor(
                        CPU_POOL, download_from_ytm, v_id
                    )

                    cache = COLD.demand_tribute(v_id)
                except asyncio.CancelledError, KeyboardInterrupt:
                    success = False
                    is_error = True
                except Exception as e:
                    is_error = True
                    LOGGER.error(f"💥Error in worker loop. Video {v_id}: {e}")

            if success and cache:
                async with self._send_semaphore:
                    R = await self._send_non_cached_to_telegram(
                        cache, title=title, artist=artist
                    )
                    is_too_large = R.is_too_large
                    is_error = R.is_error
                    file_id = R.file_id
                    await asyncio.sleep(2)
            else:
                is_error = True
            LOGGER.debug(f"Download task completed on {v_id}")

            if not is_error:
                await DM.fisting(
                    video_id=v_id, telegram_file_id=file_id, is_too_large=is_too_large
                )
            COLD.annihilate(v_id)

        futures_to_wakeup = self._active_downloads.pop(v_id, [])
        for fut in futures_to_wakeup:
            if not fut.done():
                LOGGER.debug(f"Setting result to worker tasks on {v_id}")
                fut.set_result((v_id, DownloadResult(file_id, is_too_large, is_error)))

    async def _send_non_cached_to_telegram(
        self, cache: TrackDirContentDict, *, title: str, artist: str
    ):
        """
        Returns:
            tuple: (file id or none | is too large | is error)"""
        is_too_large = False
        is_error = False
        file_id = None
        m = None
        a, tn = prepare_audio_file_to_send.prepare_audio_file_to_send(cache)
        for attempt in range(1, 4):
            try:
                LOGGER.debug(f"Sending track {title} to channel")

                m = await bot.bot.send_audio(
                    CHANNEL_STORAGE_ID,
                    audio=a,
                    thumbnail=tn,
                    title=title,
                    performer=artist,
                    request_timeout=300,
                )
                LOGGER.info(f"Send track {title} to channel")
                break

            except TelegramNetworkError as e:
                if str(e).find("Request Entity Too Large") != -1:
                    is_too_large = True
                    is_error = True

                    LOGGER.debug(f"Track {title} is too large")
                    break
                LOGGER.error(f"Network error: {e}")
                LOGGER.warning(
                    f"Sending track to channel failed on attempt {attempt}/3 (timeout after 5 min). {'Retrying in 3 seconds' if attempt < 3 else ''}"
                )
                if attempt == 3:
                    LOGGER.warning("Check your internet speed")
                    is_error = True
                    break

                await asyncio.sleep(3)
                continue

        if m and m.audio:
            file_id = m.audio.file_id
        return DownloadResult(file_id, is_too_large, is_error)

    async def _worker_loop(self) -> NoReturn:
        """Main loop."""
        LOGGER.debug(
            f"⚙️ Worker loop has been started. Slots: {self._pool_semaphore._value}"
        )

        while True:
            task = await self._queue.get()
            LOGGER.debug(f"Got new task from worker queue: {task.video_id}")

            asyncio.create_task(
                self._execute_download_task(
                    task.video_id, title=task.track_title, artist=task.artist
                )
            )

            self._queue.task_done()
