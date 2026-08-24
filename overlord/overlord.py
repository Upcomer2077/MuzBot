import asyncio
import os
import shutil
from glob import glob

from _logger import LOGGER
from schemas.dicts.dir import TrackDirContentDict


class CacheOverlord:
    """Manager for handling physical disk track directories, audio extractions, thumbnails, and cache deletions."""

    def __init__(self, cache_root: str):
        """Initialize the manager with a root storage directory pathway.

        Args:
            cache_root: Filesystem path to the root storage directory.
        """
        self._cache_dir = cache_root

    async def _lookup(self, video_id):
        """Verify the exact existence of a dedicated cache directory on disk using a track identifier.

        Args:
            video_id: Target YouTube track identifier.

        Returns:
            True if the directory exists, False otherwise.
        """
        return await asyncio.to_thread(os.path.exists, f"{self._cache_dir}/{video_id}")

    async def _get_dir_content(self, video_id: str):
        """Retrieve absolute file pathways contained within a track cached directory structure.

        Args:
            video_id: Target YouTube track identifier.

        Returns:
            A list of absolute file paths if the directory exists, otherwise None.
        """
        if await self._lookup(video_id):
            return await asyncio.to_thread(glob, f"{self._cache_dir}/{video_id}/*")

    async def demand_tribute(self, video_id: str):
        """Locate and match audio files and visual thumbnail paths within the track cache directory.

        Args:
            video_id: Target YouTube track identifier.

        Returns:
            A structured dictionary containing verified file pathways, or None if the audio file is missing.
        """
        LOGGER.debug(f"Getting directory content on {video_id}")
        content = await self._get_dir_content(video_id)

        if content is None:
            return None

        audio_path = None
        thumbnail_path = None

        for file in content:
            if file.endswith(".mp3"):
                audio_path = file
            elif file.endswith((".jpg", ".jpeg", ".webp", ".png")):
                thumbnail_path = file
        LOGGER.debug(f"Got audio and thumbnail: {audio_path}, {thumbnail_path}")
        if audio_path is None:
            return None
        return TrackDirContentDict(
            audio_path=audio_path, thumbnail_path=thumbnail_path, _video_id=video_id
        )

    async def annihilate(self, video_id: str) -> bool:
        """Permanently erase a specific track directory cache structure from disk storage blocks.

        Args:
            video_id: Target YouTube track identifier.

        Returns:
            True if the folder was successfully deleted or didn't exist, False if a permission error occurred.
        """
        p = f"{self._cache_dir}/{video_id}"
        if not await self._lookup(video_id):
            return True
        try:
            LOGGER.debug(f"Removing dir {video_id}")
            await asyncio.to_thread(shutil.rmtree, p)
            LOGGER.debug(f"Removed dir {video_id}")
            return True
        except FileNotFoundError:
            LOGGER.error(f"Cache drop error: The folder {p} does not exist")
            return False
        except PermissionError:
            LOGGER.error(f"Cache drop error: You do not have permission to delete {p}")
            return False
