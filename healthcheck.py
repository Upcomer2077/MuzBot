import asyncio
import sys

import requests

from _logger import LOGGER
from config import DATABASE_PATH, LOKI_URL
from dungeon import DM
from type import YoutubeSearchResultDict


async def _check_loki():
    LOGGER.info("---LOKI---")
    if LOKI_URL is None:
        LOGGER.info("LOKI_URL is None")
    else:
        LOGGER.info(f"LOKI_URL is {LOKI_URL}")
        ready_url = LOKI_URL.replace("/loki/api/v1/push", "/ready")
        response = await asyncio.to_thread(requests.get, ready_url, timeout=3)
        response.raise_for_status()
        # Проверяем специфичный ответ от Loki (он должен ответить текстом 'ready')
        if not response.text.strip() == "ready":
            raise (Exception("Loki is not ready"))
    return LOGGER.info("Loki check: pass")


async def _check_database():
    LOGGER.info("---DATABASE---")
    LOGGER.info(f"DB_CONTAINER_PATH: {DATABASE_PATH}")
    await DM.open_dungeon()
    res = await DM._get_slaves_count()
    LOGGER.info(f"Slaves in dungeon count: {res}")

    count_enslaved = await DM.enslave_bulk(
        [
            YoutubeSearchResultDict(
                video_id="0",
                title="0",
                artist="0",
                duration="0",
                duration_seconds=0,
            )
        ]
    )

    if count_enslaved > 0:
        LOGGER.info("Database check: passed")
        await DM.next_door(video_id="0")
    else:
        await DM.next_door(video_id="0")
        LOGGER.critical("Database check: failed. I/O error. Check your dungeon!")
        raise Exception("Database I/O error")


async def _check():
    try:
        LOGGER.info("-----HEALTH CHECK-----")
        await _check_database()
        await _check_loki()
    except Exception as e:
        LOGGER.critical(f"{e}")
        sys.exit(1)
    finally:
        await DM.next_door(video_id="0")
        await DM.close_dungeon()
        LOGGER.info("-----HEALTH CHECK END-----")


if __name__ == "__main__":
    asyncio.run(_check())
