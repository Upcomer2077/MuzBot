from _logger import LOGGER
from infra.red.redis_cache import RedisCache
from interfaces.imemcache import IMemoryCache

RED: IMemoryCache = RedisCache(LOGGER)
