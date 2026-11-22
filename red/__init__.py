from _logger import LOGGER
from interfaces.imemcache import IMemoryCache
from red.redis_cache import RedisCache

RED: IMemoryCache = RedisCache(LOGGER)
