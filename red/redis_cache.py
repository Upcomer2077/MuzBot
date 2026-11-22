from datetime import timedelta

from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio.client import Redis
from redis.exceptions import ConnectionError

from interfaces.ilogger import ILogger
from interfaces.imemcache import IMemoryCache


class RedisCache(IMemoryCache):
    def __init__(self, logger: ILogger):
        self._redis: Redis | None = None
        self.__logger = logger

    def open(self, url: str):
        self.__logger.info("Connecting redis storage...")
        self._redis = Redis.from_url(url)
        self.__logger.info("Done")

        return self._redis

    def get_storage(self, url: str):
        if not self._redis:
            self.open(url)
        else:
            return RedisStorage(redis=self._redis, state_ttl=timedelta(minutes=10))

    async def close(self):
        if self._redis:
            await self._redis.aclose()

    async def healthcheck(self) -> bool:
        try:
            if self._redis:
                await self._redis.get("test")
                return True
            return False
        except ConnectionError as e:
            self.__logger.critical(f"Failed to connect to redis: {e}")
            await self.close()
            return False
