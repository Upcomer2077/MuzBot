from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from _logger import LOGGER
from config import MAX_PLAYLIST_TRACKS_REQUEST
from dungeon.models import PlaylistCache, TrackCache, TrackPlaylist
from dungeon.repos.track import TrackRepository
from tools.extract_playlist_info import PlaylistInfoDict
from tools.types import YoutubeSearchResultDict


class PlaylistRepository:
    """Manages business operations and relational link bindings for playlist entities."""

    def __init__(self, track_repo: TrackRepository | None = None):
        self.track_repo = track_repo or TrackRepository()

    async def get_playlist(self, pl_id: str) -> PlaylistCache | None:
        """Retrieve playlist general meta information."""
        LOGGER.debug(f"Collecting info about playlist {pl_id}")
        r = await PlaylistCache.get_or_none(playlist_id=pl_id)
        LOGGER.debug(f"Collecting {pl_id} done")
        return r

    async def add_playlist_and_tracks(
        self, playlist_info: PlaylistInfoDict, tracks: list[YoutubeSearchResultDict]
    ) -> int:
        """Atomically cache a playlist structure and link incoming batch tracks."""
        async with in_transaction():
            LOGGER.debug("Adding playlist and tracks")
            count = await self.track_repo.enslave_bulk(tracks)
            LOGGER.debug(f"Tracks enslaved: {count}")

            LOGGER.debug(f"Enslaving playlist info: {playlist_info['id']} ")
            await PlaylistCache.get_or_create(
                playlist_id=playlist_info["id"],
                defaults={
                    "title": playlist_info["title"],
                    "artist": playlist_info["author"],
                },
            )

            relations_instances = [
                TrackPlaylist(
                    video_id=v["video_id"],
                    playlist_id=playlist_info["id"],
                    track_order=idx,
                )
                for (idx, v) in enumerate(tracks)
            ]

            try:
                await TrackPlaylist.bulk_create(
                    relations_instances, ignore_conflicts=True
                )
                r = len(relations_instances)
            except IntegrityError as e:
                LOGGER.warning(f"Some relations already existed: {e}")
                r = 0

            return r

    async def summon_slaves_from_playlist(
        self, playlist_id: str, limit: int | None = MAX_PLAYLIST_TRACKS_REQUEST + 1
    ) -> dict[str, TrackCache] | None:
        """Fetch all track object nodes bound to a playlist sorted sequentially."""
        LOGGER.debug(f"Getting slaves from playlist: {playlist_id} ")
        query = TrackPlaylist.filter(playlist_id=playlist_id).order_by("track_order")

        if limit is not None:
            query = query.limit(limit)

        relations = await query.prefetch_related("video")
        if not relations:
            return None

        return {r.video.video_id: r.video for r in relations if r.video}
