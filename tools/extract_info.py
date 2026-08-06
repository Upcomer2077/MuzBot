import asyncio
from typing import TYPE_CHECKING, Optional

import yt_dlp

from _logger import LOGGER
from helpers.get_ytm_video_link import get_ytm_video_link
from type import YoutubeSearchResultDict

if TYPE_CHECKING:
    from yt_dlp import _Params


async def extract_video_info(video_id: str) -> Optional[YoutubeSearchResultDict]:
    """Asynchronously extract and parse structured metadata for a specific YouTube Music video track.

    Args:
        video_id: Unique YouTube Music track video identifier.

    Returns:
        A structured dictionary with video metadata if successful, or None if extraction fails.
    """
    VIDEO = await asyncio.shield(asyncio.to_thread(_extract, video_id))

    if VIDEO:
        title: str = VIDEO.get("title") or "UNKNOWN"
        artist = ", ".join(
            [
                artist
                for artist in VIDEO.get("artists")
                or [VIDEO.get("uploader") or "unknown"]
            ]
        )
        duration: str = VIDEO.get("duration_string", "0:00")
        duration_seconds: int = int(VIDEO.get("duration", 0) or 0)

        return YoutubeSearchResultDict(
            title=title,
            artist=artist,
            video_id=video_id,
            duration=duration,
            duration_seconds=duration_seconds,
        )


def _extract(
    video_id: str,
):
    """Execute synchronous yt-dlp metadata extraction for a video without initiating a download.

    Args:
        video_id: Unique YouTube Music track video identifier.

    Returns:
        A dictionary containing raw track metadata, or None if an exception occurs.
    """
    YDL_OPTS: "_Params" = {
        "extract_flat": True,
        "no_warnings": True,
        "quiet": True,
    }
    URL = get_ytm_video_link(video_id)

    try:
        LOGGER.info(f"Extracting info about video {video_id}")
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            return ydl.extract_info(URL, download=False)

    except Exception as e:
        LOGGER.error(f"Error while getting {video_id} info: {e}")
        return None
