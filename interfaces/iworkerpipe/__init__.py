import asyncio
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from aiogram.exceptions import TelegramNetworkError

from bot.bot import bot
from config import CHANNEL_STORAGE_ID, CPU_COUNT, WORKER_CORES_COUNT
from helpers.get_hash_tags import get_hash_tags
from helpers.telegram import fetch_local_audio
from interfaces.icache import ICache
from interfaces.icache.types import TrackDirContentDict
from interfaces.idatabase import IDataBase
from interfaces.ilogger import ILogger
from interfaces.imusictools import IMusicTools
from interfaces.iworkerpipe.priorities import DownloadTaskPriorities
from interfaces.iworkerpipe.types import DownloadResult

_F = asyncio.Future[tuple[str, DownloadResult]]


@dataclass(slots=True, order=True)
class _DownloadTask:
    priority: float | DownloadTaskPriorities
    video_id: str = field(compare=False)
    track_title: str = field(compare=False)
    artist: str = field(compare=False)
    future: _F = field(default_factory=asyncio.Future, compare=False)


class IWorkerPipeline(ABC):
    def __init__(self, logger: ILogger, DM: IDataBase, COLD: ICache, MT: IMusicTools):
        self._queue: asyncio.Queue[_DownloadTask] = asyncio.PriorityQueue()
        self._q_shift = 0.0
        self._active_downloads: dict[str, list[_F]] = {}
        self._worker_task: asyncio.Task | None = None
        self._logger = logger
        self._DM = DM
        self._COLD = COLD
        self._MT = MT

        self._workers_pool_semaphore = asyncio.Semaphore(WORKER_CORES_COUNT + 3)
        """Depends on worker count (CPU threads)"""
        self._tg_upload_semaphore = asyncio.Semaphore(2)
        """Telegram upload limit per flood wait"""
        self._download_execution_semaphore = asyncio.Semaphore(10)
        """Size of batch that can be taken from queue. Prevents starvation (priorities)"""
        self._disk_space_semaphore = asyncio.Semaphore(30)
        """Saves disk space if uploading is too slow and downloading is too fast"""

        _CPUs = os.cpu_count()
        if _CPUs and (_CPUs < CPU_COUNT):
            self._logger.warning(
                f"CPU_COUNT is higher than it actually is ({CPU_COUNT} vs {_CPUs}). Worker loop freezing expected!"
            )

    def start(self):
        self._worker_task = asyncio.create_task(self._worker_loop())

    def stop(self):
        if self._worker_task:
            self._worker_task.cancel()
        self._logger.debug("Worker loop stopped.")

    async def submit(
        self,
        video_id: str,
        *,
        track_title: str,
        artist: str,
        priority: DownloadTaskPriorities,
    ):
        """Entry point. Puts task to worker loop
        Returns:
            tuple:
                v_id: video identifier

                cache: (File id, is too large, is error)

        """
        if video_id in self._active_downloads:
            self._logger.debug(f"🔗 Already downloading {video_id}. Queued...")
            fut: _F = asyncio.Future()
            self._active_downloads[video_id].append(fut)
            return await fut

        self._logger.debug(f"Appending download task to worker queue: {video_id}")
        task = _DownloadTask(
            video_id=video_id,
            track_title=track_title,
            artist=artist,
            priority=(priority + self._increase_shift()),
        )

        self._active_downloads[video_id] = [task.future]

        await self._queue.put(task)
        return await task.future

    @abstractmethod
    def download_track(self, track_id: str) -> bool: ...

    async def _execute_download_task(self, v_id: str, *, title: str, artist: str):
        """Autonomous worker task. Downloads music and sends it to telegram cache-channel"""
        is_too_large = False
        is_error = False
        file_id = None
        success = False
        cache = None

        async with self._disk_space_semaphore:
            async with self._workers_pool_semaphore:
                try:
                    self._logger.debug(f"Starting worker task on {v_id}")
                    success = await asyncio.to_thread(self.download_track, v_id)

                    cache = await self._COLD.demand_tribute(v_id)
                except asyncio.CancelledError, KeyboardInterrupt:
                    success = False
                    is_error = True
                except Exception as e:
                    is_error = True
                    self._logger.error(f"💥Error in worker loop. Video {v_id}: {e}")
                finally:
                    self._download_execution_semaphore.release()

            if success and cache:
                async with self._tg_upload_semaphore:
                    R = await self._send_non_cached_audio_to_telegram(
                        cache, title=title, artist=artist, logger=self._logger
                    )
                    is_too_large = R.is_too_large
                    is_error = R.is_error
                    file_id = R.file_id
                    await asyncio.sleep(2)
            else:
                is_error = True
            self._logger.debug(f"Download task completed on {v_id}")

            if not is_error:
                await self._DM.tracks.fisting(
                    video_id=v_id, telegram_file_id=file_id, is_too_large=is_too_large
                )
            await self._COLD.annihilate(v_id)

        futures_to_wakeup = self._active_downloads.pop(v_id, [])
        for fut in futures_to_wakeup:
            if not fut.done():
                self._logger.debug(f"Setting result to worker tasks on {v_id}")
                fut.set_result((v_id, DownloadResult(file_id, is_too_large, is_error)))

    async def _worker_loop(self):
        """Main loop."""
        self._logger.debug(
            f"⚙️ Worker loop has been started. Slots: {self._workers_pool_semaphore._value}"
        )

        while True:
            if self._queue.empty() and self._q_shift:
                self._reset_shift()
            task = await self._queue.get()
            await self._download_execution_semaphore.acquire()
            self._logger.debug(f"Got new task from worker queue: {task.video_id}")

            asyncio.create_task(
                self._execute_download_task(
                    task.video_id, title=task.track_title, artist=task.artist
                )
            )

            self._queue.task_done()

    def _increase_shift(self):
        """Increase priority micro shift to save FIFO order"""
        self._q_shift += 0.01
        return self._q_shift

    def _reset_shift(self):
        self._q_shift = 0.0

    async def _send_non_cached_audio_to_telegram(
        self, cache: TrackDirContentDict, *, title: str, artist: str, logger: ILogger
    ) -> DownloadResult:
        """
        Returns:
            tuple: (file id or none | is too large | is error)"""
        is_too_large = False
        is_error = False
        file_id = None
        m = None
        a, tn = fetch_local_audio.fetch_audio(cache)
        for attempt in range(1, 4):
            try:
                logger.debug(f"Sending track {title} to channel")
                tags = get_hash_tags(artist)
                m = await bot.send_audio(
                    CHANNEL_STORAGE_ID,
                    audio=a,
                    thumbnail=tn,
                    title=title,
                    performer=artist,
                    request_timeout=300,
                    caption=", ".join(tags),
                )
                logger.info(f"Sent track {title} to channel")
                break

            except TelegramNetworkError as e:
                if str(e).find("Request Entity Too Large") != -1:
                    is_too_large = True
                    is_error = True

                    logger.debug(f"Track {title} is too large")
                    break
                logger.error(f"Network error: {e}")
                logger.warning(
                    f"Sending track to channel failed on attempt {attempt}/3 (timeout after 5 min). {'Retrying in 3 seconds' if attempt < 3 else ''}"
                )
                if attempt == 3:
                    logger.warning("Check your internet speed")
                    is_error = True
                    break

                await asyncio.sleep(3)
                continue

        if m and m.audio:
            file_id = m.audio.file_id
        return DownloadResult(file_id, is_too_large, is_error)
