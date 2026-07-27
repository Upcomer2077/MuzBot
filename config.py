import os
from concurrent.futures import ProcessPoolExecutor

from dotenv import load_dotenv

load_dotenv("./.env.dist")

# REQUIRED
BOT_TOKEN = os.environ["BOT_TOKEN"]
# ------
# SEMI_REQUIRED
TRACKS_PER_LIMIT = max(int(os.environ["TRACKS_PER_LIMIT"]), 2)
QUERY_DOWNLOAD_LIMIT_SECS = max(int(os.environ["QUERY_DOWNLOAD_LIMIT_SECS"]), 30)
# -------------
# OPTIONAL
LOKI_URL = os.environ.get("LOKI_URL")
CPU_COUNT = int(os.environ.get("CPU_COUNT", 0)) or os.cpu_count() or 1
DB_NAME = os.environ.get("DB_NAME") or "db2"
# --------------
DATABASE_PATH = f"{os.getcwd()}/data/{DB_NAME}.db"
CACHE_ROOT_DIR = "./.cache"
CPU_POOL = ProcessPoolExecutor(max(CPU_COUNT - 1, 1), max_tasks_per_child=10)
MAX_TRACK_DURATION_SECONDS = 60 * 35
