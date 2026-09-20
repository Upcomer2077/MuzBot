import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv("./.env.dist")

# REQUIRED
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_STORAGE_ID = int(os.environ["CHANNEL_STORAGE_ID"])
"""Telegram system channel id for caching songs and backups"""
# -------------
# OPTIONAL
TRACKS_PER_LIMIT = max(int(os.environ.get("TRACKS_PER_LIMIT", "5")), 5)
"""Single (track) download request limit per user"""
QUERY_DOWNLOAD_LIMIT_SECS = max(
    int(os.environ.get("QUERY_DOWNLOAD_LIMIT_SECS", "30")), 30
)
"""Single download cooldown (flood wait)"""

PLAYLIST_DOWNLOAD_COOLDOWN_SECS = max(
    int(os.environ.get("PLAYLIST_DOWNLOAD_COOLDOWN_SECS", "20")), 20
)
"""Playlist download cooldown (flood wait)"""
PLAYLISTS_LIMIT = max(int(os.environ.get("PLAYLISTS_LIMIT", "1")), 1)
"""Playlist download request limit per user"""
PLAYLIST_MAX_TRACKS = max(int(os.environ.get("PLAYLIST_MAX_TRACKS", "0")), 0)
"""Limit of tracks in playlist that can be pulled on current machine"""

SUBSCRIPTION_COOLDOWN_SECS = max(
    int(os.environ.get("SUBSCRIPTION_COOLDOWN_SECS", "20")), 20
)
"""Subscription cooldown (flood wait)"""
SUBSCRIPTIONS_PER_LIMIT = max(int(os.environ.get("SUBSCRIPTIONS_PER_LIMIT", "4")), 4)
"""Subscription request limit per user"""

SEARCH_COOLDOWN_SECS = max(int(os.environ.get("SEARCH_COOLDOWN_SECS", "20")), 20)
"""Search cooldown (flood wait)"""
SEARCH_PER_LIMIT = max(int(os.environ.get("SEARCH_PER_LIMIT", "3")), 3)
"""Search request limit per user"""

BACKUP_EVERY_N_DAYS = max(int(os.getenv("BACKUP_EVERY_N_DAYS", "2")), 1)
"""Interval of making database file backups."""
LOKI_URL = os.environ.get("LOKI_URL")

CPU_COUNT = max(int(os.environ.get("CPU_COUNT", "0")), 0) or os.cpu_count() or 1
"""Amount of cores that can be used by app"""
DB_NAME = os.environ.get("DB_NAME") or "db2"

EXPERIMENTAL = bool(int(os.environ.get("EXPERIMENTAL", "0")))
"""Toggles experimental features (alpha and beta versions)"""
DEBUG = bool(int(os.environ.get("DEBUG", default="0")))
"""Toggles logs level and some dev features"""
TZ = ZoneInfo(os.environ.get("TZ", "Europe/Minsk"))
# ---------------------------------------------------------------

WORKER_CORES_COUNT = max(1, CPU_COUNT - 1)
"""Amount of cores that can be used as pool of workers"""
DATABASE_PATH = f"{os.getcwd()}/data/{DB_NAME}.db"
CACHE_ROOT_DIR = "./.cache"
"""Process pool executor main instance"""
MAX_TRACK_DURATION_SECONDS = 60 * 35
MAX_PLAYLIST_TRACKS_REQUEST = 300
"""Max limit of tracks in playlist that can be fetched from ytm"""
PAGINATION_ITEMS_PER_PAGE = 9
"""Limit of results on one page"""
# ---------------------------------------------------------------

SHOW_ON_STARTUP: dict[str, str | int] = {
    "CHANNEL_STORAGE_ID": CHANNEL_STORAGE_ID,
    "TRACKS_PER_LIMIT": TRACKS_PER_LIMIT,
    "QUERY_DOWNLOAD_LIMIT_SECS": QUERY_DOWNLOAD_LIMIT_SECS,
    "BACKUP_EVERY_N_DAYS": BACKUP_EVERY_N_DAYS,
    "CPU_COUNT": CPU_COUNT,
    "DATABASE_CONTAINER_PATH": DATABASE_PATH,
    "PLAYLISTS_LIMIT": PLAYLISTS_LIMIT,
    "PLAYLIST_DOWNLOAD_COOLDOWN_SECS": PLAYLIST_DOWNLOAD_COOLDOWN_SECS,
    "PLAYLIST_MAX_TRACKS": PLAYLIST_MAX_TRACKS,
    "SUBSCRIPTION_COOLDOWN_SECS": SUBSCRIPTION_COOLDOWN_SECS,
    "SUBSCRIPTIONS_PER_LIMIT": SUBSCRIPTIONS_PER_LIMIT,
    "SEARCH_COOLDOWN_SECS": SEARCH_COOLDOWN_SECS,
    "SEARCH_PER_LIMIT": SEARCH_PER_LIMIT,
    "DEBUG": DEBUG,
}
