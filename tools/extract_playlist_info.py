import asyncio
import random

from _logger import LOGGER
from config import MAX_PLAYLIST_TRACKS_REQUEST
from schemas.dicts import PlaylistInfoDict, YoutubeSearchResultDict
from tools.YTMusic_client import YT


async def extract_playlist_info(
    playlist_id: str,
) -> tuple[PlaylistInfoDict, list[YoutubeSearchResultDict]] | None:
    """Asynchronously extract and parse structured metadata for a specific YouTube Music video track.

    Args:
        video_id: Unique YouTube Music track video identifier.

    Returns:
        A structured dictionary with video metadata if successful, or None if extraction fails.
    """
    LOGGER.debug(f"Extracting info about playlist {playlist_id}")

    async with YT.playlist_lock:
        await asyncio.sleep(random.uniform(1.0, 3.0))
        PLAYLIST = await asyncio.to_thread(_extract, playlist_id)

    LOGGER.debug(f"Info about playlist {bool(PLAYLIST)}")
    if PLAYLIST is None or "tracks" not in PLAYLIST:
        return None

    videos: list[YoutubeSearchResultDict] = []
    info: list = PLAYLIST["tracks"]

    author: str | None = "unknown"
    if playlist_id.startswith("OLAK5uy_"):
        author = ", ".join([a["name"] for a in info[0].get("artists", [])])
    elif playlist_id.startswith(("PL", "RD")):
        author = PLAYLIST.get("author", {}).get("name", None)

    for track in info:
        if not track.get("videoId"):
            continue
        _artists = ", ".join([a["name"] for a in track["artists"]])

        videos.append(
            YoutubeSearchResultDict(
                title=track.get("title") or "UNKNOWN",
                artist=_artists.replace(" - Topic", ""),
                video_id=track.get("videoId"),
                duration=track.get("duration"),
                duration_seconds=track.get("duration_seconds") or 0,
            )
        )
    playlist_title: str | None = PLAYLIST.get("title", None)
    if playlist_title:
        playlist_title = playlist_title.replace("Album - ", "")

    return (
        PlaylistInfoDict(title=playlist_title, id=PLAYLIST["id"], author=author),
        videos,
    )


def _extract(link: str):
    """Execute synchronous metadata extraction for a video without initiating a download.

    Args:
        link: YouTube Music track video link.

    Returns:
        A dictionary containing raw track metadata, or None if an exception occurs.
    """
    try:
        return YT.get_playlist(link, limit=MAX_PLAYLIST_TRACKS_REQUEST)

    except Exception:
        return
