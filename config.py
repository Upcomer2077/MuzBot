import os
from concurrent.futures import ProcessPoolExecutor

from dotenv import load_dotenv

load_dotenv("./.env.dist")

# REQUIRED
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_STORAGE_ID = int(os.environ["CHANNEL_STORAGE_ID"])
# ------
# SEMI_REQUIRED
TRACKS_PER_LIMIT = max(int(os.environ["TRACKS_PER_LIMIT"]), 2)
QUERY_DOWNLOAD_LIMIT_SECS = max(int(os.environ["QUERY_DOWNLOAD_LIMIT_SECS"]), 30)
# -------------
# OPTIONAL
BACKUP_EVERY_N_DAYS = max(int(os.getenv("BACKUP_EVERY_N_DAYS", 2)), 1)
LOKI_URL = os.environ.get("LOKI_URL")
CPU_COUNT = max(int(os.environ.get("CPU_COUNT", 0)), 0) or os.cpu_count() or 1
DB_NAME = os.environ.get("DB_NAME") or "db2"
REPLY_DISAPPEAR_TIMEOUT = max(int(os.environ.get("REPLY_DISAPPEAR_TIMEOUT", 0)), 30)
# --------------
DATABASE_PATH = f"{os.getcwd()}/data/{DB_NAME}.db"
CACHE_ROOT_DIR = "./.cache"
CPU_POOL = ProcessPoolExecutor(max(CPU_COUNT - 1, 1), max_tasks_per_child=10)
MAX_TRACK_DURATION_SECONDS = 60 * 35

_SHOW_ON_STARTUP: dict[str, str | int] = {
    "CHANNEL_STORAGE_ID": CHANNEL_STORAGE_ID,
    "TRACKS_PER_LIMIT": TRACKS_PER_LIMIT,
    "QUERY_DOWNLOAD_LIMIT_SECS": QUERY_DOWNLOAD_LIMIT_SECS,
    "BACKUP_EVERY_N_DAYS": BACKUP_EVERY_N_DAYS,
    "CPU_COUNT": CPU_COUNT,
    "DATABASE_CONTAINER_PATH": DATABASE_PATH,
}
