from abc import ABC, abstractmethod

from interfaces.icache.types import TrackDirContentDict


class ICache(ABC):
    """Manager for handling physical disk track directories, audio extractions, thumbnails, and cache deletions."""

    @abstractmethod
    async def lookup(self, track_id) -> bool:
        """Verify the exact existence of a dedicated cache directory on disk using a track identifier.

        Args:
            video_id: Target YouTube track identifier.

        Returns:
            True if the directory exists, False otherwise.
        """

    @abstractmethod
    async def demand_tribute(self, track_id: str) -> None | TrackDirContentDict:
        """Locate and match audio files and visual thumbnail paths within the track cache directory.

        Args:
            video_id: Target YouTube track identifier.

        Returns:
            A structured dictionary containing verified file pathways, or None if the audio file is missing.
        """

    @abstractmethod
    async def annihilate(self, track_id: str) -> bool:
        """Permanently erase a specific track directory cache structure from disk storage blocks.

        Args:
            video_id: Target YouTube track identifier.

        Returns:
            True if the folder was successfully deleted or didn't exist, False if a permission error occurred.
        """
