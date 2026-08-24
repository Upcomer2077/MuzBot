import asyncio
import random

from _logger import LOGGER
from schemas.dicts import YoutubeSearchResultDict
from tools.YTMusic_client import YT


async def extract_video_info(video_id: str) -> YoutubeSearchResultDict | None:
    """Asynchronously extract and parse structured metadata for a specific YouTube Music video track.

    Args:
        video_id: Unique YouTube Music track video identifier.

    Returns:
        A structured dictionary with video metadata if successful, or None if extraction fails.
    """
    LOGGER.debug(f"Extracting info about {video_id}")

    async with YT.track_lock:
        await asyncio.sleep(random.uniform(1.0, 2.0))
        VIDEO = await asyncio.to_thread(_extract, video_id)

    LOGGER.debug(f"Has info about {video_id}: {bool(VIDEO)}")

    if VIDEO:
        title: str = VIDEO.get("title") or "UNKNOWN"
        artist = VIDEO.get("author") or "unknown"
        duration_seconds: int = int(VIDEO.get("lengthSeconds", 0) or 0)

        return YoutubeSearchResultDict(
            title=title,
            artist=artist,
            video_id=video_id,
            duration=None,
            duration_seconds=duration_seconds,
        )


def _extract(
    video_id: str,
) -> dict[str, str] | None:
    """Execute synchronous metadata extraction for a video without initiating a download.

    Args:
        video_id: Unique YouTube Music track video identifier.

    Returns:
        A dictionary containing raw track metadata, or None if an exception occurs.
    """

    try:
        LOGGER.info(f"Extracting info about video {video_id}")
        return YT.get_song(videoId=video_id).get("videoDetails", None)

    except Exception as e:
        LOGGER.error(f"Error while getting {video_id} info: {e}")
        return None
