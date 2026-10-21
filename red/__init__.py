from config import REDIS_CACHE_URL
from red.redis_cache import RedisCache

RED = RedisCache(REDIS_CACHE_URL)
