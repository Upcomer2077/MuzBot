import asyncio
from typing import TYPE_CHECKING, Optional

import yt_dlp
from yt_dlp.utils import PagedList

from _logger import LOGGER
from helpers.get_ytm_video_link import get_ytm_playlist_link
from tools.extract_info import extract_video_info
from type import PlaylistInfoDict, YoutubeSearchResultDict

if TYPE_CHECKING:
    from yt_dlp import _Params


async def extract_playlist_info(
    playlist_id: str,
) -> Optional[tuple[PlaylistInfoDict, list[YoutubeSearchResultDict]]]:
    """Asynchronously extract and parse structured metadata for a specific YouTube Music video track.

    Args:
        video_id: Unique YouTube Music track video identifier.

    Returns:
        A structured dictionary with video metadata if successful, or None if extraction fails.
    """
    LOGGER.debug(f"Extracting info about playlist {playlist_id}")

    PLAYLIST = await asyncio.shield(
        asyncio.to_thread(_extract, get_ytm_playlist_link(playlist_id))
    )
    LOGGER.debug(f"Info about playlist {bool(PLAYLIST)}")

    if PLAYLIST is None or "entries" not in PLAYLIST:
        return None
    videos: list[YoutubeSearchResultDict] = []

    info = (
        PLAYLIST["entries"].getpage(1)
        if isinstance(PLAYLIST["entries"], PagedList)
        else PLAYLIST["entries"]
    )
    # ====== ;( =======
    artist = None
    for track in info:
        v = await extract_video_info(track.get("id"))
        if (
            not v
            or v.get("artist").lower().find("release") != -1
            or v.get("artist").lower().find("topic") != -1
        ):
            continue
        artist = v.get("artist")

        break
    # ================

    for track in info:
        _artist = artist
        _a = track.get("uploader") or track.get("channel")
        if _a and _a.lower().find("release") == -1:
            _artist = _a
        videos.append(
            YoutubeSearchResultDict(
                title=track.get("title") or "UNKNOWN",
                artist=(_artist or "unknown").replace(" - Topic", ""),
                video_id=track.get("id"),
                duration="0",
                duration_seconds=track.get("duration") or 0,
            )
        )
    playlist_title = PLAYLIST.get("title", None)
    if playlist_title:
        playlist_title = playlist_title.replace("Album - ", "")

    return (
        PlaylistInfoDict(title=playlist_title, id=PLAYLIST["id"], artist=artist),
        videos,
    )


def _extract(link: str):
    """Execute synchronous yt-dlp metadata extraction for a video without initiating a download.

    Args:
        video_id: Unique YouTube Music track video identifier.

    Returns:
        A dictionary containing raw track metadata, or None if an exception occurs.
    """
    YDL_OPTS: "_Params" = {
        "extract_flat": True,
        "no_warnings": True,
        # TODO: config?
        "playlistend": 30,
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
