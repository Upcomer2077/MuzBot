import shutil
from glob import glob

from _logger import LOGGER
from config import CACHE_ROOT_DIR
from type import TrackDirContentDict


class CacheOverlord:
    def __init__(self, cache_root: str):
        self._cache_dir = cache_root

    def _lookup(self, video_id):
        return len(glob(f"{self._cache_dir}/{video_id}")) == 1

    def _get_dir_content(self, video_id: str):
        if self._lookup(video_id):
            return glob(f"{self._cache_dir}/{video_id}/*")

    def demand_tribute(self, video_id: str):
        content = self._get_dir_content(video_id)

        if content is None:
            return None

        audio_path = None
        thumbnail_path = None

        for file in content:
            if file.endswith(".mp3"):
                audio_path = file
            elif file.endswith((".jpg", ".jpeg", ".webp", ".png")):
                thumbnail_path = file

        if audio_path is None:
            return None
        return TrackDirContentDict(audio_path=audio_path, thumbnail_path=thumbnail_path)

    def annihilate(self, video_id: str) -> bool:
        p = f"{self._cache_dir}/{video_id}"
        if not self._lookup(video_id):
            return True
        try:
            shutil.rmtree(p)
            return True
        except FileNotFoundError:
            LOGGER.error(f"Cache drop error: The folder {p} does not exist")
            return False
        except PermissionError:
            LOGGER.error(f"Cache drop error: You do not have permission to delete {p}")
            return False


COLD = CacheOverlord(CACHE_ROOT_DIR)
