from ytmusicapi import YTMusic

from _logger import LOGGER
from schemas.dicts import YoutubeSearchResultDict


def search_in_ytm(search_query: str, limit: int = 10):
    """Search for song items using the YouTube Music API and normalize the returned metadata.

    Args:
        search_query: The search term or keywords specified by the user.
        limit: Maximum number of search records to return. Defaults to 10.

    Returns:
        A list of structured dictionaries containing normalized song metadata and video identifiers.
    """
    YT = YTMusic()
    LOGGER.debug(f"Extracting info query: {search_query}")

    try:
        SEARCH_RESULTS = YT.search(query=search_query, filter="songs", limit=limit)
        LOGGER.debug(f"Found info query: {bool(SEARCH_RESULTS)}")
    except Exception:
        LOGGER.critical(f'Can\'t pull info from "{search_query}" query')
    video_ids: list[YoutubeSearchResultDict] = []

    for item in SEARCH_RESULTS[: min(limit, 10)]:
        title: str = item.get("title") or "Unknown"
        artist = ", ".join([artist["name"] for artist in item.get("artists", [])])
        video_id: str | None = item.get("videoId") or None
        duration: str = item.get("duration") or "0:00"
        duration_seconds: int = item.get("duration_seconds", 0) or 0

        if video_id:
            video_ids.append(
                YoutubeSearchResultDict(
                    title=title,
                    artist=artist,
                    video_id=video_id,
                    duration=duration,
                    duration_seconds=duration_seconds,
                )
            )

    return video_ids
