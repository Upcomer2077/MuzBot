import asyncio
from typing import TYPE_CHECKING

import yt_dlp

from helpers.get_ytm_video_link import get_ytm_video_link
from type import YoutubeSearchResultDict

if TYPE_CHECKING:
    from yt_dlp import _Params


async def extract_info(video_id: str):

    url = get_ytm_video_link(video_id)

    ydl_opts: "_Params" = {
        "extract_flat": True,  # Не зарываться в форматы, только метаданные
        "no_warnings": True,
        "quiet": True,
    }

    def _extract():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)

        except Exception as e:
            print(f"Видео {video_id} недоступно или удалено: {e}")
            return None

    item = await asyncio.shield(asyncio.to_thread(_extract))

    if not item:
        return None

    title: str = item.get("title") or "Unknown"
    artist = ", ".join(
        [
            artist
            for artist in item.get("artists") or [item.get("uploader") or "Unknown"]
        ]
    )
    duration: str = item.get("duration_string", "0:00")
    duration_seconds: int = int(item.get("duration", 0) or 0)

    return YoutubeSearchResultDict(
        title=title,
        artist=artist,
        video_id=video_id,
        duration=duration,
        duration_seconds=duration_seconds,
    )
