import asyncio
from random import uniform
from typing import Final

from _logger import LOGGER
from tools.types import ArtistConcreteEntityInfoDict, ArtistInfoDict
from tools.YTMusic_client import YT


async def extract_artist_discography(
    artist_id: str, *, top_only=True
) -> ArtistInfoDict | None:
    """Asynchronously extract and parse structured metadata for a specific YouTube Music video track.

    Args:
        video_id: Unique YouTube Music track video identifier.

    Returns:
        A structured dictionary with video metadata if successful, or None if extraction fails.
    """

    LOGGER.debug(f"Extracting info about author {artist_id}")
    try:
        INFO = await asyncio.to_thread(YT.get_artist, artist_id)
    except Exception as e:
        LOGGER.error(f"Error in extract_artist_discography: {e}")
        return None
    LOGGER.debug(f"Has info about {artist_id}: {bool(INFO)}")
    albums: list[ArtistConcreteEntityInfoDict] = INFO.get("albums", {}).get(
        "results", None
    )

    singles: list[ArtistConcreteEntityInfoDict] = INFO.get("singles", {}).get(
        "results", None
    )

    if not top_only:
        if singles and len(singles):
            if "params" in INFO["singles"] and "browseId" in INFO["singles"]:
                singles_params: str = INFO["singles"]["params"]
                try:
                    await asyncio.sleep(uniform(1, 2))

                    MORE_INFO_SINGLES = await asyncio.to_thread(
                        YT.get_artist_albums,
                        INFO["singles"]["browseId"],
                        singles_params,
                    )
                    if len(MORE_INFO_SINGLES):
                        singles: list[ArtistConcreteEntityInfoDict] = [
                            {
                                "title": i["title"],
                                "browseId": i["browseId"],
                                "audioPlaylistId": i["playlistId"],
                                "order": len(MORE_INFO_SINGLES) - idx,
                            }
                            for idx, i in enumerate(MORE_INFO_SINGLES, start=1)
                        ]
                except Exception as e:
                    LOGGER.error(f"Error in extract_artist_discography: {e}")
            else:
                try:
                    _singles: list[ArtistConcreteEntityInfoDict] = []
                    for idx, i in enumerate(singles, start=1):
                        await asyncio.sleep(uniform(1, 3))
                        a = await asyncio.to_thread(YT.get_album, i["browseId"])
                        _singles.append(
                            {
                                "audioPlaylistId": a["audioPlaylistId"],
                                "browseId": i["browseId"],
                                "title": a["title"],
                                "order": len(singles) - idx,
                            }
                        )
                    if len(_singles):
                        singles = _singles
                except Exception as e:
                    LOGGER.error(f"Error in extract_artist_discography: {e}")

        # +======
        if albums and len(albums):
            if "params" in INFO["albums"] and "browseId" in INFO["albums"]:
                albums_params: str = INFO["albums"]["params"]
                try:
                    await asyncio.sleep(uniform(1, 2))

                    MORE_INFO_ALBUMS: Final = await asyncio.to_thread(
                        YT.get_artist_albums, INFO["albums"]["browseId"], albums_params
                    )

                    if len(MORE_INFO_ALBUMS):
                        albums = [
                            {
                                "title": i["title"],
                                "browseId": i["browseId"],
                                "audioPlaylistId": i["playlistId"],
                                "order": len(MORE_INFO_ALBUMS) - idx,
                            }
                            for idx, i in enumerate(MORE_INFO_ALBUMS, start=1)
                        ]
                except Exception as e:
                    LOGGER.error(f"Error in extract_artist_discography: {e}")
            else:
                for idx, i in enumerate(albums, start=1):
                    i["order"] = len(albums) - idx

    else:
        if albums and len(albums):
            _albums: list[ArtistConcreteEntityInfoDict] = [
                {
                    "title": i["title"],
                    "browseId": i["browseId"],
                    "audioPlaylistId": i["audioPlaylistId"],
                    "order": len(albums) - idx,
                }
                for idx, i in enumerate(albums, start=1)
            ]
            albums = _albums
        if singles and len(singles):
            try:
                _singles: list[ArtistConcreteEntityInfoDict] = []
                for idx, i in enumerate(singles, start=1):
                    await asyncio.sleep(uniform(1, 3))

                    c = await asyncio.to_thread(YT.get_album, i["browseId"])
                    _singles.append(
                        {
                            "audioPlaylistId": c["audioPlaylistId"],
                            "browseId": i["browseId"],
                            "title": c["title"],
                            "order": len(singles) - idx,
                        }
                    )
                if len(_singles):
                    singles = _singles
            except Exception as e:
                LOGGER.error(f"Error in extract_artist_discography: {e}")

    return ArtistInfoDict(
        albums=albums,
        singles=singles,
        name=INFO["name"],
    )
