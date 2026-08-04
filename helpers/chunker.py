import asyncio

from _logger import LOGGER
from config import CPU_COUNT
from dungeon.models import TrackCache
from helpers.pull_data_from_cache import pull_data_from_cache


async def chunked_downloader(tracks: list[TrackCache]):
    """
    Асинхронный генератор. Делит треки на пачки по `k`,
    скачивает их через gather(return_exceptions=True) и отдает наружу.
    """
    k = max(CPU_COUNT - 1, 1)
    for i in range(0, len(tracks), k):
        chunk = tracks[i : i + k]

        # Создаем задачи строго для ТЕКУЩЕЙ пачки (в пуле не будет висеть лишнего мусора)
        tasks = [pull_data_from_cache(v.video_id) for v in chunk]

        LOGGER.info(f"⚡ Запуск gather для пачки из {len(tasks)} треков...")

        # Обязательно return_exceptions=True, чтобы один сбойный трек не рушил весь плейлист
        chunk_results = await asyncio.gather(*tasks, return_exceptions=False)

        # Возвращаем готовую пачку, жестко сохранив исходный порядок
        yield chunk_results
