import asyncio

from tools.types import ArtistsShortInfoDict
from tools.YTMusic_client import YT


async def search_artists_in_ytm(performer: str) -> list[ArtistsShortInfoDict]:

    resp = await asyncio.to_thread(YT.search, performer, filter="artists", limit=3)

    result: list[ArtistsShortInfoDict] = []

    for p in resp[:15]:
        result.append({"name": p["artist"], "id": p["browseId"]})

    return result
