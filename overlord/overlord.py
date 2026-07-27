import shutil
from glob import glob

from _logger import LOGGER
from type import TrackDirContentDict


class CacheOverlord:
    """Manager for handling physical disk track directories, audio extractions, thumbnails, and cache deletions."""

    def __init__(self, cache_root: str):
        """Initialize the manager with a root storage directory pathway.

        Args:
            cache_root: Filesystem path to the root storage directory.
        """
        self._cache_dir = cache_root

    def _lookup(self, video_id):
        """Verify the exact existence of a dedicated cache directory on disk using a track identifier.

        Args:
            video_id: Target YouTube track identifier.

        Returns:
            True if the directory exists, False otherwise.
        """
        return len(glob(f"{self._cache_dir}/{video_id}")) == 1

    def _get_dir_content(self, video_id: str):
        """Retrieve absolute file pathways contained within a track cached directory structure.

        Args:
            video_id: Target YouTube track identifier.

        Returns:
            A list of absolute file paths if the directory exists, otherwise None.
        """
        if self._lookup(video_id):
            return glob(f"{self._cache_dir}/{video_id}/*")

    def demand_tribute(self, video_id: str):
        """Locate and match audio files and visual thumbnail paths within the track cache directory.

        Args:
            video_id: Target YouTube track identifier.

        Returns:
            A structured dictionary containing verified file pathways, or None if the audio file is missing.
        """
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
        """Permanently erase a specific track directory cache structure from disk storage blocks.

        Args:
            video_id: Target YouTube track identifier.

        Returns:
            True if the folder was successfully deleted or didn't exist, False if a permission error occurred.
        """
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
