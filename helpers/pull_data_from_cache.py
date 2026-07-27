import asyncio

from _logger import LOGGER
from config import CPU_POOL
from overlord import COLD
from tools.download import download_from_ytm


async def pull_data_from_cache(video_id: str):
    """Retrieve track media assets from disk cache or download them via an asynchronous thread pool if missing.

    Args:
        video_id: Unique YouTube Music track video identifier.

    Returns:
        A dictionary with audio and thumbnail paths if retrieved successfully, False otherwise.
    """
    cache_data = False
    cache_data = COLD.demand_tribute(video_id)
    if cache_data:
        return cache_data

    loop = asyncio.get_event_loop()
    try:
        success = await loop.run_in_executor(CPU_POOL, download_from_ytm, video_id)
    except Exception as e:
        LOGGER.warn(f"Error while running in executor!!! {e}")
    if not success:
        return False

    return COLD.demand_tribute(video_id) or False
