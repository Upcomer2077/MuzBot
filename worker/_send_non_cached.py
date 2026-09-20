import asyncio

from aiogram.exceptions import TelegramNetworkError

import bot
from _logger import LOGGER
from config import CHANNEL_STORAGE_ID
from helpers import fetch_local_audio
from overlord.types import TrackDirContentDict
from worker.types import DownloadResult


async def send_non_cached_audio_to_telegram(
    cache: TrackDirContentDict, *, title: str, artist: str
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
            LOGGER.debug(f"Sending track {title} to channel")

            m = await bot.bot.send_audio(
                CHANNEL_STORAGE_ID,
                audio=a,
                thumbnail=tn,
                title=title,
                performer=artist,
                request_timeout=300,
            )
            LOGGER.info(f"Sent track {title} to channel")
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
