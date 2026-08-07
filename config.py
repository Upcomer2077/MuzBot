import os
from concurrent.futures import ProcessPoolExecutor

from dotenv import load_dotenv

load_dotenv("./.env.dist")

# REQUIRED
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_STORAGE_ID = int(os.environ["CHANNEL_STORAGE_ID"])
# -------------
# OPTIONAL
TRACKS_PER_LIMIT = max(int(os.environ.get("TRACKS_PER_LIMIT", 2)), 2)
QUERY_DOWNLOAD_LIMIT_SECS = max(
    int(os.environ.get("QUERY_DOWNLOAD_LIMIT_SECS", 30)), 30
)

PLAYLIST_DOWNLOAD_COOLDOWN_SECS = max(
    int(os.environ.get("PLAYLIST_DOWNLOAD_COOLDOWN_SECS", 20)), 20
)
PLAYLISTS_LIMIT = max(int(os.environ.get("PLAYLISTS_LIMIT", 1)), 1)

BACKUP_EVERY_N_DAYS = max(int(os.getenv("BACKUP_EVERY_N_DAYS", 2)), 1)
LOKI_URL = os.environ.get("LOKI_URL")

CPU_COUNT = max(int(os.environ.get("CPU_COUNT", 0)), 0) or os.cpu_count() or 1
DB_NAME = os.environ.get("DB_NAME") or "db2"

EXPERIMENTAL = bool(int(os.environ.get("EXPERIMENTAL", 0)))
DEBUG = bool(int(os.environ.get("DEBUG", 0)))
# ---------------------------------------------------------------

WORKER_CORES_COUNT = max(1, CPU_COUNT - 1)
DATABASE_PATH = f"{os.getcwd()}/data/{DB_NAME}.db"
CACHE_ROOT_DIR = "./.cache"
CPU_POOL = ProcessPoolExecutor(WORKER_CORES_COUNT)
MAX_TRACK_DURATION_SECONDS = 60 * 35
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
    "DEBUG": DEBUG,
}
