from datetime import datetime

from peewee_aio import Manager

from _logger import LOGGER
from config import MAX_TRACK_DURATION_SECONDS
from dungeon.dispatcher import DB_DISPATCHER
from dungeon.models import PlaylistCache, TrackCache, TrackPlaylist
from type import PlaylistInfoDict, YoutubeSearchResultDict


class DungeonMaster:
    """Database controller managing TrackCache operations, schema initializations, and bulk entries."""

    def __init__(self, db_path: str, db_dispatcher: Manager):
        """Initialize database credentials and assign the peewee-async manager instance.

        Args:
            db_path: Filesystem path to the SQLite database.
            db_dispatcher: Asynchronous database connection manager.
        """

        self._db_path = db_path
        self._db_dispatcher = db_dispatcher

    async def open_dungeon(
        self,
    ):
        """Open database connection, initialize tables, set PRAGMA optimizations, and reset temporary states."""

        try:
            async with self._db_dispatcher:
                async with self._db_dispatcher.connection():
                    await TrackCache.create_table(safe=True)
                    await PlaylistCache.create_table(safe=True)
                    await TrackPlaylist.create_table(safe=True)
                    await self._db_dispatcher.execute("PRAGMA journal_mode=WAL;")
                    await self._db_dispatcher.execute("PRAGMA synchronous=NORMAL;")
                    await self._db_dispatcher.execute("PRAGMA foreign_keys=ON;")
                    await self._db_dispatcher.execute(
                        "PRAGMA auto_vacuum = INCREMENTAL;"
                    )
            await self._finalize()
        except Exception as e:
            LOGGER.critical(f"Caught error while opening the dungeon: {e}")

    async def close_dungeon(self):
        """Reset operational database states and disconnect safely from the storage engine."""

        await self._finalize()
        await self._db_dispatcher.disconnect()

    async def enslave_bulk(self, tracks: list[YoutubeSearchResultDict]) -> int:
        """Insert multiple tracks into the cache database in a single batch query.

        Args:
            tracks: Collection of dictionaries containing YouTube Music search result data.

        Returns:
            The total number of successfully inserted database rows.
        """

        if not tracks:
            return 0

        try:
            data_to_insert = []

            for track in tracks:
                data_to_insert.append(
                    {
                        TrackCache.video_id: track["video_id"],
                        TrackCache.title: track["title"],
                        TrackCache.artist: track["artist"],
                        TrackCache.track_duration: int(track["duration_seconds"]),
                        TrackCache.is_too_large: int(
                            (track["duration_seconds"] or 0)
                            > MAX_TRACK_DURATION_SECONDS
                        ),
                    }
                )

            query = TrackCache.insert_many(data_to_insert)

            inserted_rows: int = await self._db_dispatcher.execute(query)
            return inserted_rows

        except Exception as e:
            LOGGER.error(f"Bulk saving error: {e}")
            return 0

    async def summon_slaves(self, video_ids: list[str]) -> dict[str, TrackCache]:
        """Fetch cached Telegram file identifiers mapping them to their corresponding video identifiers.

        Args:
            video_ids: List of YouTube track video identifiers to query.

        Returns:
            A dictionary mapping matching video IDs to available Telegram file IDs.
        """
        query = TrackCache.select().where(TrackCache.video_id.in_(video_ids))

        rows = await query

        res: dict[str, TrackCache] = {}
        for i in rows:
            if i.video_id:
                res[i.video_id] = i
        return res

    async def summon_one(self, video_id: str):
        """Retrieve a specific track record and update its recent usage timestamp indicator.

        Args:
            video_id: Target YouTube track identifier.

        Returns:
            The TrackCache model object instance if found, otherwise None.
        """
        try:
            track = await TrackCache.get_or_none(TrackCache.video_id == video_id)
            if track:
                track.last_used_at = datetime.now()
                await track.save()

                return track
            return None
        except Exception as e:
            LOGGER.error(f"Can't find track {video_id} in database: {e}")
            return None

    async def next_door(self, video_id: str) -> bool:
        """Delete a specific track cache record completely from the database using its identifier.

        Args:
            video_id: Target YouTube track identifier to purge.

        Returns:
            True if the target row was deleted successfully, False if not found or failed.
        """
        try:
            query = TrackCache.delete().where(TrackCache.video_id == video_id)
            deleted_count = await self._db_dispatcher.execute(query)
            return deleted_count > 0
        except Exception as e:
            LOGGER.error(f"Can't delete track {video_id}: {e}")
            return False

    async def fisting(
        self,
        video_id: str | list[str],
        telegram_file_id: str | None = None,
        is_too_large: bool | None = None,
        is_work_in_progress: bool | None = None,
    ) -> bool:
        """Update attribute states, processing status flags, or Telegram properties on a specific track.

        Args:
            video_id: Target YouTube track identifier.
            telegram_file_id: Unique Telegram cloud storage file reference. Defaults to None.
            is_too_large: Constraint flag indicating file size exceeded limits. Defaults to None.
            is_work_in_progress: Download concurrency lock status flag. Defaults to None.

        Returns:
            True if any database records were modified, False otherwise.
        """

        update_data = {
            TrackCache.telegram_file_id: telegram_file_id,
            TrackCache.is_too_large: is_too_large,
            TrackCache.is_work_in_progress: is_work_in_progress,
        }
        filtered_update_data = {k: v for k, v in update_data.items() if v is not None}
        try:
            query = TrackCache.update(filtered_update_data).where(
                TrackCache.video_id.in_(video_id)
                if isinstance(video_id, list)
                else TrackCache.video_id == video_id
            )

            rows_updated: int = await self._db_dispatcher.execute(query)
            return rows_updated != 0

        except Exception as e:
            LOGGER.error(f"Caught error while updating records: {e}")
            return False

    async def _get_slaves_count(self):
        """Calculate and return the absolute number of track records currently present in the table.

        Returns:
            Total row count integer from the tracks table.
        """
        res = await TrackCache.select(TrackCache.video_id).count()
        return res

    async def add_playlist_and_tracks(
        self, playlist_info: PlaylistInfoDict, tracks: list[YoutubeSearchResultDict]
    ):
        await self.enslave_bulk(tracks)
        q1 = PlaylistCache.insert(
            playlist_id=playlist_info["id"], title=playlist_info["title"]
        )
        _ = await DB_DISPATCHER.execute(q1)
        relations_data = [
            {
                "video_id": v["video_id"],
                "playlist_id": playlist_info["id"],
                "track_order": idx,
            }
            for (idx, v) in enumerate(tracks)
        ]
        q2 = TrackPlaylist.insert_many(relations_data).on_conflict_ignore()
        r: int = await DB_DISPATCHER.execute(q2)
        return r

    async def summon_slaves_from_playlist(
        self, playlist_id: str
    ) -> dict[str, TrackCache]:
        """Fetch cached Telegram file identifiers mapping them to their corresponding video identifiers.

        Args:
            playlist_id: ytm playlist identifier to query.

        Returns:
            A dictionary mapping matching video IDs to available Telegram file IDs.
        """
        query = (
            TrackCache.select()
            .join(TrackPlaylist, on=(TrackCache.video_id == TrackPlaylist.video_id))
            .where(TrackPlaylist.playlist_id == playlist_id)
            .order_by(TrackPlaylist.track_order)
        )

        rows = await query

        res: dict[str, TrackCache] = {}
        for i in rows:
            if i.video_id:
                res[i.video_id] = i
        return res

    async def _finalize(self):
        """Reset temporary runtime processing flags globally across all tracks back to inactive states."""
        query = TrackCache.update(is_work_in_progress=False).where(
            TrackCache.is_work_in_progress == True  # noqa: E712
        )
        try:
            await self._db_dispatcher.execute(query)
        except Exception as e:
            LOGGER.error(f"❌ Не удалось обновить базу данных при выключении: {e}")
