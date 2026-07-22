import os
import re

from dotenv import load_dotenv

load_dotenv("./.env.dist")

BOT_TOKEN = os.environ["BOT_TOKEN"]
CACHE_ROOT_DIR = os.environ["CACHE_ROOT_DIR"]
DATABASE_PATH = os.environ["DATABASE_PATH"]

INLINE_STOP_WORD = "%"
MAX_TRACK_DURATION_SECONDS = 60 * 35
YTM_REGEX = re.compile(
    r"(?:https?:\/\/)?music\.youtube\.com/watch\?.*v=([a-zA-Z0-9_\-]{11})"
)
YTM_VID_REGEX = re.compile(
    r"v=([a-zA-Z0-9_\-]{11})",
)
