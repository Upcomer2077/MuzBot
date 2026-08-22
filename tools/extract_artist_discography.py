import asyncio

from ytmusicapi import YTMusic

from _logger import LOGGER
from schemas.dicts.artist import ArtistInfoDict


async def extract_artist_discography(artist_id: str) -> ArtistInfoDict:
    """Asynchronously extract and parse structured metadata for a specific YouTube Music video track.

    Args:
        video_id: Unique YouTube Music track video identifier.

    Returns:
        A structured dictionary with video metadata if successful, or None if extraction fails.
    """
    YT = YTMusic()

    LOGGER.debug(f"Extracting info about author {artist_id}")

    INFO = await asyncio.to_thread(YT.get_artist, artist_id)
    LOGGER.debug(f"Has info about {artist_id}: {bool(INFO)}")

    return ArtistInfoDict(
        albums=INFO.get("albums", None),
        singles=INFO.get("singles", None),
        name=INFO["name"],
    )
