from _logger import LOGGER
from config import CACHE_ROOT_DIR
from infra.overlord.overlord import CacheOverlord
from interfaces.icache import ICache

COLD: ICache = CacheOverlord(CACHE_ROOT_DIR, LOGGER)
"""Global CacheOverlord instance handling local filesystem interactions for media storage files."""
