import asyncio
from collections.abc import AsyncGenerator

from config import CPU_COUNT
from dungeon.models import TrackCache
from helpers.pull_data_from_cache import pull_data_from_cache
from type import TrackDirContentDict


async def chunked_downloader(
    tracks: list[TrackCache],
) -> AsyncGenerator[list[tuple[str, TrackDirContentDict] | tuple[str, None]]]:

    k = max(CPU_COUNT - 1, 1)
    for i in range(0, len(tracks), k):
        chunk = tracks[i : i + k]

        tasks = [pull_data_from_cache(v.video_id) for v in chunk]

        chunk_results = await asyncio.gather(*tasks, return_exceptions=False)

        yield chunk_results
