import asyncio
from dataclasses import dataclass, field
from typing import NamedTuple, NoReturn, Optional

from aiogram.exceptions import TelegramNetworkError

import bot
from _logger import LOGGER
from config import CHANNEL_STORAGE_ID, CPU_COUNT, CPU_POOL
from helpers import prepare_audio_file_to_send
from overlord import COLD
from tools.download import download_from_ytm
from type import TrackDirContentDict


@dataclass
class DownloadTask:
    video_id: str
    track_title: str
    artist: str
    future: asyncio.Future[tuple[str, _DownloadResult]] = field(
        default_factory=asyncio.Future
    )


class _DownloadResult(NamedTuple):
    file_id: Optional[str]
    is_too_large: bool
    is_error: bool


class WorkerPipe:
    def __init__(self):
        self._queue: asyncio.Queue[DownloadTask] = asyncio.Queue()
        self._active_downloads: dict[
            str, list[asyncio.Future[tuple[str, _DownloadResult]]]
        ] = {}
        self._pool_semaphore = asyncio.Semaphore(max(1, CPU_COUNT - 1))
        self._worker_task: Optional[asyncio.Task] = None

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
            fut: asyncio.Future[tuple[str, _DownloadResult]] = asyncio.Future()
            self._active_downloads[video_id].append(fut)
            return await fut

        LOGGER.debug(f"Appending download task to worker queue: {video_id}")
        task = DownloadTask(video_id=video_id, track_title=track_title, artist=artist)
        self._active_downloads[video_id] = [task.future]

        await self._queue.put(task)
        return await task.future

    async def _execute_download_task(self, v_id: str, *, title: str, artist: str):
        """Autonomous worker task. Downloads music and sends it to telegram cache-channel"""
        is_too_large = False
        is_error = False
        file_id = None
        async with self._pool_semaphore:
            try:
                LOGGER.debug(f"Starting worker task on {v_id}")
                loop = asyncio.get_event_loop()
                success = await loop.run_in_executor(CPU_POOL, download_from_ytm, v_id)
                cache = COLD.demand_tribute(v_id)
                if success and cache:
                    (
                        file_id,
                        is_too_large,
                        is_error,
                    ) = await self._send_non_cached_to_telegram(
                        cache, title=title, artist=artist
                    )
                else:
                    is_error = True
                LOGGER.debug(f"Download task completed on {v_id}")

            except Exception as e:
                is_error = True
                LOGGER.error(f"💥Error in worker loop. Video {v_id}: {e}")

        COLD.annihilate(v_id)

        futures_to_wakeup = self._active_downloads.pop(v_id, [])
        for fut in futures_to_wakeup:
            if not fut.done():
                LOGGER.debug(f"Setting result to worker tasks on {v_id}")
                fut.set_result((v_id, _DownloadResult(file_id, is_too_large, is_error)))

    async def _send_non_cached_to_telegram(
        self, cache: TrackDirContentDict, *, title: str, artist: str
    ):
        """
        Returns:
            tuple: (file id or none | is too large | is error)"""
        is_too_large = False
        is_error = False
        file_id = None
        a, tn = prepare_audio_file_to_send.prepare_audio_file_to_send(cache)
        try:
            LOGGER.debug(f"Sending track {title} to channel")

            m = await bot.bot.send_audio(
                CHANNEL_STORAGE_ID, audio=a, thumbnail=tn, title=title, performer=artist
            )
            LOGGER.debug(f"Send track {title} to channel")

        except TelegramNetworkError as e:
            if e.message.find("Request Entity Too Large") != -1:
                is_too_large = True
                LOGGER.debug(f"Track {title} is too large")

            LOGGER.error(f"Network error: {e}")
            is_error = True
        finally:
            if m.audio:
                file_id = m.audio.file_id
        return (file_id, is_too_large, is_error)

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
