import asyncio
from random import uniform

from helpers.utils import U
from tools.types import YoutubeSearchResultDict
from tools.YTMusic_client import YT


async def get_watch_pl(video_id: str) -> list[YoutubeSearchResultDict] | None:

    async with YT.rec_lock:
        await asyncio.sleep(uniform(1, 2))
        resp = await asyncio.to_thread(
            YT.get_watch_playlist, videoId=video_id, limit=25
        )

    tracks = resp["tracks"]

    if not tracks or isinstance(tracks, str):
        return None

    result: list[YoutubeSearchResultDict] = [
        YoutubeSearchResultDict(
            video_id=i["videoId"],
            title=i["title"],
            duration=i["length"],
            artist=", ".join(a["name"] for a in i["artists"]),
            duration_seconds=U.time_to_seconds(i["length"]),
        )
        for i in tracks[1:]
    ]

    return result
