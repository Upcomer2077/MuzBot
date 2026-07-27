from config import CACHE_ROOT_DIR
from overlord.overlord import CacheOverlord

COLD = CacheOverlord(CACHE_ROOT_DIR)
"""Global CacheOverlord instance handling local filesystem interactions for media storage files."""
