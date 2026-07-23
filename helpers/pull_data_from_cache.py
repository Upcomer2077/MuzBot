import asyncio
from typing import Callable

from config import CPU_POOL
from overlord import COLD


async def pull_data_from_cache(video_id: str, download: Callable[[str], bool]):
    cache_data = False
    cache_data = COLD.demand_tribute(video_id)
    if cache_data:
        return cache_data

    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(CPU_POOL, download, video_id)
    if not success:
        return False

    return COLD.demand_tribute(video_id) or False
