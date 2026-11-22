from abc import ABC, abstractmethod

from interfaces.ilogger import ILogger
from tools.types import (
    ArtistInfoDict,
    ArtistsShortInfoDict,
    PlaylistInfoDict,
    SearchResultDict,
)


class IMusicTools(ABC):
    def __init__(self, *, logger: ILogger):
        self._logger = logger

    @abstractmethod
    def download_track(self, track_id: str) -> bool:
        """Download audio tracks from YouTube Music and convert them into MP3 format along with thumbnails.

        Args:
            video_id: Unique YouTube Music track video identifier.

        Returns:
            True if the download and conversion complete successfully, False otherwise.
        """

    @abstractmethod
    async def extract_artist_discography(
        self, artist_id: str, top_only: bool = True
    ) -> ArtistInfoDict | None:
        """Asynchronously extract and parse structured metadata for a specific YouTube Music video track.

        Args:
            video_id: Unique YouTube Music track video identifier.

        Returns:
            A structured dictionary with video metadata if successful, or None if extraction fails.
        """

    @abstractmethod
    async def extract_track_info(self, track_id: str) -> SearchResultDict | None:
        """Asynchronously extract and parse structured metadata for a specific YouTube Music video track.

        Args:
            video_id: Unique YouTube Music track video identifier.

        Returns:
            A structured dictionary with video metadata if successful, or None if extraction fails.
        """

    @abstractmethod
    async def extract_playlist_info(
        self,
        playlist_id: str,
    ) -> tuple[PlaylistInfoDict, list[SearchResultDict]] | None:
        """Asynchronously extract and parse structured metadata for a specific YouTube Music video track.

        Args:
            video_id: Unique YouTube Music track video identifier.

        Returns:
            A structured dictionary with video metadata if successful, or None if extraction fails.
        """

    @abstractmethod
    async def get_like_pl(self, track_id: str) -> list[SearchResultDict] | None: ...

    @abstractmethod
    async def search_artists_in(self, performer: str) -> list[ArtistsShortInfoDict]: ...

    @abstractmethod
    async def search_track_in(
        self, search_query: str, limit: int = 27 * 2
    ) -> list[SearchResultDict]:
        """Search for song items using the YouTube Music API and normalize the returned metadata.

        Args:
            search_query: The search term or keywords specified by the user.
            limit: Maximum number of search records to return. Defaults to 10.

        Returns:
            A list of structured dictionaries containing normalized song metadata and video identifiers.
        """
