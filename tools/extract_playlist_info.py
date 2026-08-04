import asyncio
from typing import TYPE_CHECKING, Optional

import yt_dlp
from yt_dlp.utils import PagedList

from type import PlaylistInfoDict, YoutubeSearchResultDict

if TYPE_CHECKING:
    from yt_dlp import _Params


async def extract_playlist_info(
    link: str,
) -> Optional[tuple[PlaylistInfoDict, list[YoutubeSearchResultDict]]]:
    """Asynchronously extract and parse structured metadata for a specific YouTube Music video track.

    Args:
        video_id: Unique YouTube Music track video identifier.

    Returns:
        A structured dictionary with video metadata if successful, or None if extraction fails.
    """
    PLAYLIST = await asyncio.shield(asyncio.to_thread(_extract, link))
    if PLAYLIST is None or "entries" not in PLAYLIST:
        return None
    videos: list[YoutubeSearchResultDict] = []

    info = (
        PLAYLIST["entries"].getpage(1)
        if isinstance(PLAYLIST["entries"], PagedList)
        else PLAYLIST["entries"]
    )
    for track in info:
        videos.append(
            YoutubeSearchResultDict(
                title=track.get("title") or "UNKNOWN",
                artist=(
                    track.get("uploader") or track.get("channel") or "unknown"
                ).replace(" - Topic", ""),
                video_id=track.get("id"),
                duration="0",
                duration_seconds=track.get("duration") or 0,
            )
        )
    return (
        PlaylistInfoDict(title=PLAYLIST.get("title", None), id=PLAYLIST["id"]),
        videos,
    )


def _extract(link: str, limit: int | None = None):
    """Execute synchronous yt-dlp metadata extraction for a video without initiating a download.

    Args:
        video_id: Unique YouTube Music track video identifier.

    Returns:
        A dictionary containing raw track metadata, or None if an exception occurs.
    """
    YDL_OPTS: "_Params" = {
        "extract_flat": True,
        "no_warnings": True,
        "playlistend": None if limit is None else max(1, min(limit, 30)),
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            return ydl.extract_info(
                link,
                download=False,
            )

    except Exception:
        return None
