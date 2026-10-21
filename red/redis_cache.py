from datetime import timedelta

from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio.client import Redis
from redis.exceptions import ConnectionError

from _logger import LOGGER


class RedisCache:
    def __init__(self, url: str):
        self._redis = self._get_redis(url)

    def _get_redis(self, url: str):
        LOGGER.debug("Connecting redis storage...")
        redis_client = Redis.from_url(url)

        LOGGER.info("Done")
        return redis_client

    def get_redis_storage(self):
        return RedisStorage(redis=self._redis, state_ttl=timedelta(minutes=10))

    async def open(self):
        try:
            await self._redis.get("test")
        except ConnectionError as e:
            LOGGER.critical(f"Failed to connect to redis: {e}")
            await self.close()

    async def close(self):
        await self._redis.aclose()
