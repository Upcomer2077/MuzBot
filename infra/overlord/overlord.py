import asyncio
import shutil
from pathlib import Path

from interfaces.icache import ICache
from interfaces.icache.types import TrackDirContentDict
from interfaces.ilogger import ILogger


class CacheOverlord(ICache):
    def __init__(self, cache_root: str, logger: ILogger):
        """Initialize the manager with a root storage directory pathway.

        Args:
            cache_root: Filesystem path to the root storage directory.
        """
        self._cache_dir = cache_root
        self.__logger = logger

    async def lookup(self, track_id):
        target_dir = Path(self._cache_dir) / track_id
        return await asyncio.to_thread(target_dir.is_dir)

    async def _get_dir_content(self, track_id: str):
        """Retrieve absolute file pathways contained within a track cached directory structure.

        Args:
            video_id: Target YouTube track identifier.

        Returns:
            A list of absolute file paths if the directory exists, otherwise None.
        """
        if await self.lookup(track_id):
            target_dir = Path(self._cache_dir) / track_id
            return await asyncio.to_thread(
                lambda: [str(p) for p in target_dir.iterdir()]
            )

    async def demand_tribute(self, track_id: str) -> None | TrackDirContentDict:
        self.__logger.debug(f"Getting directory content on {track_id}")
        content = await self._get_dir_content(track_id)

        if content is None:
            return None

        audio_path = None
        thumbnail_path = None

        for file in content:
            if file.endswith(".mp3"):
                audio_path = file
            elif file.endswith((".jpg", ".jpeg", ".webp", ".png")):
                thumbnail_path = file
        self.__logger.debug(f"Got audio and thumbnail: {audio_path}, {thumbnail_path}")
        if audio_path is None:
            self.__logger.error(f"Audio path oа track {track_id} is None")
            return None
        return TrackDirContentDict(
            audio_path=audio_path, thumbnail_path=thumbnail_path, _track_id=track_id
        )

    async def annihilate(self, track_id: str) -> bool:

        p = f"{self._cache_dir}/{track_id}"
        if not await self.lookup(track_id):
            return True
        try:
            self.__logger.debug(f"Removing dir {track_id}")
            await asyncio.to_thread(shutil.rmtree, p)
            self.__logger.debug(f"Removed dir {track_id}")
            return True
        except FileNotFoundError:
            self.__logger.error(f"Cache drop error: The folder {p} does not exist")
            return False
        except PermissionError:
            self.__logger.error(
                f"Cache drop error: You do not have permission to delete {p}"
            )
            return False
