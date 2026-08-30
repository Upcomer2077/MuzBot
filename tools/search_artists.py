import asyncio

from ytmusicapi import YTMusic

from schemas.dicts.artist import ArtistsShortInfoDict


async def search_artists_in_ytm(performer: str) -> list[ArtistsShortInfoDict]:
    YT = YTMusic()

    resp = await asyncio.to_thread(YT.search, performer, filter="artists", limit=3)

    result: list[ArtistsShortInfoDict] = []

    for p in resp[:9]:
        result.append({"name": p["artist"], "id": p["browseId"]})

    return result
