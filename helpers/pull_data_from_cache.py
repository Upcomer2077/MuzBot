import asyncio
from typing import Callable

from overlord import COLD


async def pull_data_from_cache(video_id: str, download: Callable[[str], bool]):
    cache_data = False
    while not cache_data:
        cache_data = COLD.demand_tribute(video_id)
        if not cache_data:
            if not await asyncio.shield(asyncio.to_thread(download, video_id)):
                return False
    return cache_data
