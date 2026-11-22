from _logger import LOGGER
from config import CACHE_ROOT_DIR
from interfaces.icache import ICache
from overlord.overlord import CacheOverlord

COLD: ICache = CacheOverlord(CACHE_ROOT_DIR, LOGGER)
"""Global CacheOverlord instance handling local filesystem interactions for media storage files."""
